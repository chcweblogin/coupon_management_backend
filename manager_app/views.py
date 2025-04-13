# views.py
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth.models import User
from vso_app.models import Coupon, DoctorPersonalDetails, Settlement, Transaction, TransactionDetail, VSOPersonalDetails
from vso_app.serializers import DoctorSerializer, VSOPersonalDetailsSerializer, VSOSerializer
from .models import ManagerPersonalDetails
from .serializers import ManagerPersonalDetailsSerializer
from django.db.models import Sum, Count
from rest_framework.exceptions import NotFound
from django.utils.timezone import now
from django.views.generic import TemplateView


#dashboard
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    
class VSODashboardAPIView(View):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # If dates not provided, default to today's date
        if not start_date or not end_date:
            today = now().date()
            start_date = end_date = str(today)

        # Filtered data
        coupons = Coupon.objects.filter(date_collected__range=[start_date, end_date],status='collected'
        )
        transactions = Transaction.objects.filter(date_transaction__range=[start_date, end_date],status='redeemed'
        )
        doctors = DoctorPersonalDetails.objects.all()
        vsos = VSOPersonalDetails.objects.all()


        vso_stats = coupons.values('vso__name').annotate(coupons=Sum('coupon_points'))
          # Convert queryset to list for JSON serialization

        product_stats = coupons.values('product__name').annotate(coupons=Sum('coupon_points'))
        
        
        # Get all VSOs
        vsos = VSOPersonalDetails.objects.all()

        # Final result list
        vso_summary = []

        for vso in vsos:
            # 1. Get all transactions done by this VSO in date range
            vso_transactions = Transaction.objects.filter(
                vso=vso.vso_id,
                date_transaction__range=(start_date, end_date),

            ).values('doctor_id', 'date_transaction').distinct()

            # 2. Count distinct call days per doctor
            doctor_calls = (
                vso_transactions.values('doctor_id')
                .annotate(total_call_days=Count('date_transaction', distinct=True))
            )

            # 3. Total calls = sum of call days across doctors
            total_calls = sum([item['total_call_days'] for item in doctor_calls])

            # 4. Total coupons collected by this VSO in date range
            total_coupons = Coupon.objects.filter(
                vso=vso.vso_id,
                date_collected__range=(start_date, end_date)
                ,status='collected'
        
            ).aggregate(total=Sum('coupon_points'))['total'] or 0

            # 5. Format doctors' call data
            doctors_data = [
                
                {
                    'doctor_name': DoctorPersonalDetails.objects.get(doctor_id=entry['doctor_id']).name,
                    'call_count': entry['total_call_days']
                }
                for entry in doctor_calls
            ]

            # 6. Append to final list
            vso_summary.append({
                'vso_name': vso.name,
                'coupons': total_coupons,
                'calls': total_calls,
                'doctors': doctors_data
            })

        
        data = {
            'total_coupons': coupons.aggregate(total=Sum('coupon_points'))['total'] or 0,
            'points_redeemed': transactions.aggregate(total=Sum('total_points_used'))['total'] or 0,
            'doctor_count': doctors.count(),
            'vso_count': vsos.count(),
            'start_date': start_date,
            'end_date': end_date,
            'vso_stats': list(vso_stats),

  'product_stats':list(product_stats),

        'vso_coverage': vso_summary
        }

        #VSO-wise coupon collection stats
        


        

        return JsonResponse(data)

# Create your views here.
class ManagerProfileAPIView(APIView):
    
    # Get a manager profile by `manager_id`
    def get(self, request, manager_id=None):
        if manager_id:
            try:
                manager = ManagerPersonalDetails.objects.get(manager_id=manager_id)
                serializer = ManagerPersonalDetailsSerializer(manager)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ManagerPersonalDetails.DoesNotExist:
                return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            managers = ManagerPersonalDetails.objects.all()
            serializer = ManagerPersonalDetailsSerializer(managers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

   
    def post(self, request):
        # Attempt to retrieve the user by email
        
        # Add the user object to request data
        manager_data = request.data.copy()  # Ensure you're not modifying the original request.data
        #manager_data['email'] = user.email

        # Serialize and validate Manager data
        manager_serializer = ManagerPersonalDetailsSerializer(data=manager_data)
        if manager_serializer.is_valid():
            manager_instance = manager_serializer.save()
            # Add manager's ID to the request data for the VSO profile
            vso_data = request.data.copy()  # Separate data for VSO
            vso_data['manager'] = manager_instance.manager_id

            # Create VSO profile
            
            vso_serializer = VSOSerializer(data=vso_data)
            if vso_serializer.is_valid():
                
                vso_serializer.save()

                # Return both manager and VSO data in response
                return Response( manager_serializer.data,
                 status=status.HTTP_201_CREATED)
            else:
                

                return Response(vso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(manager_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Update an existing manager profile
    def put(self, request, manager_id):
        try:
            # Retrieve the manager instance
            manager = ManagerPersonalDetails.objects.get(manager_id=manager_id)
            
            # Retrieve the associated VSO instance
            vso = VSOPersonalDetails.objects.get(vso_id=manager.vso_id)
            
            # Update ManagerPersonalDetails
            manager_serializer = ManagerPersonalDetailsSerializer(
                manager, data=request.data, partial=True
            )
            
            # Add the manager reference for the VSO update
            vso_data = request.data.copy()
            vso_data['manager'] = manager.manager_id  # Pass the manager ID as the foreign key
            
            # Update VSOPersonalDetails
            vso_serializer = VSOSerializer(vso, data=vso_data, partial=True)
            
            if manager_serializer.is_valid() and vso_serializer.is_valid():
                manager_serializer.save()
                vso_serializer.save()
                
                # Return updated manager data
                return Response(manager_serializer.data, status=status.HTTP_200_OK)
            
            # Return validation errors
            errors = {
                "manager_errors": manager_serializer.errors,
                "vso_errors": vso_serializer.errors,
            }
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ManagerPersonalDetails.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except VSOPersonalDetails.DoesNotExist:
            return Response({"error": "VSO not found"}, status=status.HTTP_404_NOT_FOUND)

    # Delete a manager profile
    def delete(self, request, manager_id):
        try:
            manager = ManagerPersonalDetails.objects.get(manager_id=manager_id)
            manager.delete()
            return Response({"message": "Manager deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ManagerPersonalDetails.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)




class DoctorsUnderVSO(APIView):
    def get(self, request, vso_id):
        # Filter doctors by vso_id
        doctors = DoctorPersonalDetails.objects.filter(vso_id=vso_id)

        if not doctors.exists():
            return Response({"error": "No doctors found for the given VSO."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize doctor data
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class VSOAndDoctorFilterView(APIView):
    def get(self, request, *args, **kwargs):
        # Get filter parameters
        district = request.query_params.get('district', None)
        taluka = request.query_params.get('taluka', None)
        gavthan = request.query_params.get('gavthan', None)
        name = request.query_params.get('name', None)
        filter_type = request.query_params.get('type', 'both')  # Can be 'vso', 'doctor', or 'both'
        

        # Build query based on filters
        vso_filter = Q()
        doctor_filter = Q()

        if district:
            vso_filter &= Q(district__iexact=district)
            doctor_filter &= Q(district__iexact=district)
        if taluka:
            vso_filter &= Q(taluka__iexact=taluka)
            doctor_filter &= Q(taluka__iexact=taluka)
        if gavthan:
            vso_filter &= Q(gavthan__iexact=gavthan)
            doctor_filter &= Q(gavthan__iexact=gavthan)
        if name:
            vso_filter &= Q(name__icontains=name)
            doctor_filter &= Q(name__icontains=name)

        current_username = request.user
        # Step 2: Filter manager details based on username
        manager = ManagerPersonalDetails.objects.get(email=current_username)

        # Initialize response data
        data = {}

        # Filter VSO records if requested
        if filter_type in ['vso', 'both']:
            vso_queryset = VSOPersonalDetails.objects.filter(vso_filter,manager_id=manager.manager_id)
            vso_serializer = VSOSerializer(vso_queryset, many=True)
            data['VSOs'] = vso_serializer.data

        # Filter Doctor records if requested
        if filter_type in ['doctor', 'both']:
            doctor_queryset = DoctorPersonalDetails.objects.filter(doctor_filter,vso_id=manager.vso_id)
            doctor_serializer = DoctorSerializer(doctor_queryset, many=True)
            data['Doctors'] = doctor_serializer.data

        # Return combined data
        return Response(data)

class ManagerAnalysisAPIView(APIView):

    def get(self, request):
        # Retrieve the date and manager ID from query parameters
        date = request.query_params.get('date')
        manager_id = request.query_params.get('manager_id')

        if not date or not manager_id:
            return Response({"error": "Both date and manager_id must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the date from string format to a date object
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Get all VSOs assigned to the manager
        vsos = VSOPersonalDetails.objects.filter(manager_id=manager_id)

        # Initialize data structure to hold summary for each VSO
        vso_summary_data = []

        for vso in vsos:
            vso_id = vso.vso_id

            # Calculate total coupon points collected by this VSO
            total_collected = Transaction.objects.filter(
                vso_id=vso_id,
                date_transaction__gte=selected_date
            ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

            # Calculate total coupon points redeemed by this VSO
            total_redeemed = Settlement.objects.filter(
                vso_id=vso_id,
                date_settled__gte=selected_date
            ).aggregate(Sum('points_settled_value'))['points_settled_value__sum'] or 0

            # Calculate total customer calls by this VSO
            total_calls = Transaction.objects.filter(
                vso_id=vso_id,
                date_transaction__gte=selected_date
            ).count()

            # Add VSO summary data to the list
            vso_summary_data.append({
                "vso_name": vso.name,
                "total_points_collected": total_collected,
                "total_calls": total_calls,
                "total_points_redeemed": total_redeemed
            })

        # Prepare the response with summary data for each VSO
        response_data = {
            "manager_id": manager_id,
            "vso_summary": vso_summary_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
