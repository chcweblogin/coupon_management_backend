from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from django.db.models import Sum, Count,F
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Subquery, OuterRef,  F
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.db import transaction as db_transaction
from manager_app.models import ManagerPersonalDetails
from manager_app.serializers import ManagerPersonalDetailsSerializer

from .models import  BonusRecords, BonusSettlement, Coupon, CreditRepayment, CreditRepaymentDetail, DoctorCredit, DoctorPersonalDetails,  Gifts, Product, Settlement, StockTransaction, Transaction, TransactionDetail, VSOPersonalDetails, VSOProductStock

from .serializers import BonusSettlementSerializer, CouponRedeemSerializer, CouponSerializer, CouponSerializerPOST, CustomAuthTokenSerializer, DoctorCreditSerializer, DoctorPersonalDetailsSerializer, DoctorSerializer, LoginSerializer, ProductSerializer, SettlementSerializer,  TransactionDetailSerializer, TransactionSerializer, UserSerializer, VSOPersonalDetailsSerializer, VSOSerializer
# Create your views here.


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            
        except UserModel.DoesNotExist:
            return None
        if user.password==password:
            return user
        return None
    
class CheckAuthStatus(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        return Response({'is_authenticated': True})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['username']  # Change to email
            password = serializer.validated_data['password']
            
            # Authenticate the user using email
            user = authenticate(request, username=email, password=password)

            
            if user is not None:
                # Create or get token for the user
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "user_id": user.id,
                    "username": user.username,
                    "token": token.key,
                }, status=status.HTTP_200_OK)

            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView (APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        logout(request)
        return Response({'is_authenticated': False},status=status.HTTP_200_OK)
    

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "username": serializer.data.get("username"),
                "token": token.key,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Generate a password reset link and send it to the user
            reset_link = f"http://your-domain.com/reset-password?email={email}"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        return Response({"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)




class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)



#VSO Management Views
class VSOCreation(APIView):
    def post(self, request):
        
        serializer = VSOSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VSOList(APIView):
    def get(self, request):
        vsos = VSOPersonalDetails.objects.all()
        serializer = VSOSerializer(vsos, many=True)
        return Response(serializer.data)


class VSOUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        vso = VSOPersonalDetails.objects.get(vso_id=id)
        serializer = VSOSerializer(vso)
        return Response(serializer.data)
    
   
    def put(self, request, vso_id=None):  # Change 'id' to 'vso_id'
        try:
            # Retrieve the existing VSO instance by vso_id
            vso = VSOPersonalDetails.objects.get(vso_id=vso_id)
        except VSOPersonalDetails.DoesNotExist:
            return Response({"error": "VSO not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VSOSerializer(vso, data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        vso = VSOPersonalDetails.objects.get(vso_id=id)
        vso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    


# Create your views here.
class DoctorListCreate(APIView):
    
    def get(self, request):
        doctors = DoctorPersonalDetails.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
class ManagerContact(APIView):
    
    def get(self, request):
        # Get the VSO ID from the query parameters
        vso_id = request.query_params.get('vsoID')
        print(vso_id)

        if not vso_id:
            return Response({"error": "vsoID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the VSO object
            vso = VSOPersonalDetails.objects.get(vso_id=vso_id) if vso_id else None

            # Fetch the Manager object using the 'as_manager' field from the VSO object
            manager = ManagerPersonalDetails.objects.get(manager_id=vso.manager.manager_id)

            # Return the manager's contact number
            return Response({"contact_number": manager.contact_no}, status=status.HTTP_200_OK)

        except VSOPersonalDetails.DoesNotExist:
            return Response({"error": "VSO not found"}, status=status.HTTP_404_NOT_FOUND)

        except ManagerPersonalDetails.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class DoctorDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        doctor = DoctorPersonalDetails.objects.get(doctor_id=doctor_id)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    def patch(self, request, doctor_id=None):
        doctor = get_object_or_404(DoctorPersonalDetails, doctor_id=doctor_id)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPersonalInfoView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        role = request.query_params.get('role')

        if not email or not role:
            return Response({"error": "Email and role are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'manager':
            user_info = get_object_or_404(ManagerPersonalDetails, email__username=email)
            serializer = ManagerPersonalDetailsSerializer(user_info)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif role == 'vso':
            user_info = get_object_or_404(VSOPersonalDetails, email__username=email)
            serializer = VSOPersonalDetailsSerializer(user_info)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif role == 'doctor':
            user_info = get_object_or_404(DoctorPersonalDetails, email__username=email)
            serializer = DoctorPersonalDetailsSerializer(user_info)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid role specified. Valid roles are: manager, vso, doctor."},
                            status=status.HTTP_400_BAD_REQUEST)

        

    
#Product Management Views
class ProductListCreate(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(product_id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        try:
            product = Product.objects.get(product_id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            product = Product.objects.get(product_id=id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RedeemableProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get(self, request):
        # Retrieve coupon points from query parameters
        coupon_points = request.query_params.get('coupon_points')

        # Check if coupon_points is provided and is a valid number
        if coupon_points is not None:
            try:
                coupon_points = float(coupon_points)
                # Filter products where settlement_points is less than coupon_points
                products = Product.objects.all()
            except ValueError:
                return Response({'error': 'Invalid coupon points value'}, status=400)
        else:
            # If no coupon_points provided, return all products (optional)
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


#Coupon Management Views
class CouponListCreate(APIView):
    
    

    def get(self, request):
        # Retrieve doctor_id from the query parameters
        doctor_id = request.query_params.get('doctor_id')

        # Check if doctor_id is provided
        if not doctor_id:
            return Response({'Invalid input': 'doctor id not provided'}, status=400)

        # Subquery to get the latest coupon for each product
        latest_coupons = Coupon.objects.filter(
            product_id=OuterRef('product_id'),
            doctor_id=doctor_id,
            
        ).order_by('-date_collected', '-time_collected').values('coupon_id')[:1]

        # Filter coupons based on the most recent records per product
        coupons = (
            Coupon.objects.filter(coupon_id__in=Subquery(latest_coupons),current_points__gt=0)
            .annotate(
                product_name=F('product__name'),
                settlement_points=F('product__settlement_points'),
                coupon_value=F('product__coupon_value'),
                latest_transaction_date=F('date_collected'),
                latest_transaction_time=F('time_collected'),
            )
            .order_by('-latest_transaction_date', '-latest_transaction_time')
        )

        # Serialize and return the results
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Add coupons for a doctor, ensure negative balance is covered,
        and create transaction and transaction details.
        """
        data = request.data
        doctor_id = data.get('doctor')
        vso_id = data.get('vso')
        product_id = data.get('product')
        coupon = int(data.get('coupon_points', 0))
        status_ = data.get('status')

        print(f"Received data: {data}")

        if not (doctor_id and coupon > 0 and status_):
            return Response(
                {"detail": "Doctor ID, coupon points > 0, and status are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with db_transaction.atomic():
                # Retrieve doctor, VSO, and product
                doctor = DoctorPersonalDetails.objects.get(doctor_id=doctor_id)
                vso = VSOPersonalDetails.objects.get(vso_id=vso_id) if vso_id else None
                product = Product.objects.get(product_id=product_id) if product_id else None

                # Check existing coupon points
                existing_coupon = Coupon.objects.filter(product=product, doctor_id=doctor_id).order_by('-date_collected', '-time_collected').first()
                existing_coupon_points = existing_coupon.current_points if existing_coupon else 0

                # Create a transaction
                transaction = Transaction.objects.create(
                    vso=vso,
                    doctor=doctor,
                    total_points_used=coupon,
                    date_transaction=timezone.now().date(),
                    time_transaction=timezone.now().time(),
                    status=status_,
                )

                # Create a transaction detail record
                TransactionDetail.objects.create(
                    transaction=transaction,
                    product=product,
                    previous_points=existing_coupon_points,
                    points_used=coupon,
                    quantity_redeemed=1,
                )


                try:
                    # Bonus point calculation
                    bonus_points_for_product = coupon * (product.bonus_points or 0)
                    print(f"Calculated bonus points: {bonus_points_for_product}")

                    # Validate manager
                    manager = vso.manager
                    if not manager:
                        print("VSO does not have an associated manager.")
                        raise ValueError("VSO does not have an associated manager.")

                    # Update or create bonus record
                    with db_transaction.atomic():
                        bonus_record, created = BonusRecords.objects.get_or_create(manager=manager)
                        bonus_record.current_bonus_points = bonus_record.current_bonus_points +  bonus_points_for_product
                        bonus_record.save()
                        print("Bonus record updated successfully.")
                except Exception as e:
                    print(f"Error updating bonus record: {e}")

                # Add coupon record
                coupon_ = Coupon.objects.create(
                    doctor=doctor,
                    vso=vso,
                    product=product,
                    status="collected",
                    coupon_points=coupon,
                    current_points=existing_coupon_points + coupon,
                    transaction=transaction,
                )

                


                return Response(
                    {
                        "couponPoints": coupon_.coupon_points,
                        "status": coupon_.status,
                        "vso": coupon_.vso.vso_id if coupon_.vso else None,
                        "doctor": coupon_.doctor.doctor_id,
                        "product": coupon_.product.product_id if coupon_.product else None,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except DoctorPersonalDetails.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        except VSOPersonalDetails.DoesNotExist:
            return Response({"detail": "VSO not found."}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




def collect_coupons(doctor, vso, product, points, existing_coupon, points_summary, transaction):
    """
    Handle the logic for collecting coupons.
    """
    # Add coupon record
    Coupon.objects.create(
        doctor=doctor,
        vso=vso,
        product=product,
        status="collected",
        coupon_points=points,
        current_points=(existing_coupon.current_points + points if existing_coupon else points),
        transaction=transaction,  # Link to the transaction
    )

    # Update points summary after collection
    if points_summary.remaining_points < 0:
        # Offset negative balance first
        negative_balance = abs(points_summary.remaining_points)
        if points >= negative_balance:
            points_summary.remaining_points = points - negative_balance
        else:
            points_summary.remaining_points += points
    else:
        # Simply add points to remaining balance
        points_summary.remaining_points += points

    points_summary.total_points += points
    points_summary.save()

def redeem_coupons(doctor, vso, product, points, existing_coupon, points_summary, transaction):
    """
    Handle the logic for redeeming coupons.
    """
    if points_summary.remaining_points >= points:
        # Add coupon record
        Coupon.objects.create(
            doctor=doctor,
            vso=vso,
            product=product,
            status="redeemed",
            coupon_points=points,
            current_points=(existing_coupon.current_points - points if existing_coupon else 0),
            transaction=transaction,  # Link to the transaction
        )

        # Update points summary
        points_summary.remaining_points -= points
        points_summary.used_points += points
        points_summary.save()
    else:
        raise ValueError("Not enough points to redeem.")








class CouponDetail(APIView):
    def get(self, request, id):
        coupon = Coupon.objects.get(coupon_id=id)
        serializer = CouponSerializer(coupon)
        return Response(serializer.data)

    def put(self, request, id):
        coupon = Coupon.objects.get(coupon_id=id)
        serializer = CouponSerializer(coupon, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        coupon = Coupon.objects.get(coupon_id=id)
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



# Coupon API
class CouponAPIView(APIView):
    def get(self, request):
        coupons = Coupon.objects.all()
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Transaction API
class TransactionAPIView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Settlement API
class SettlementAPIView(APIView):
    def get(self, request):
        # Retrieve doctor_id, count, and query from query parameters
        doctor_id = request.query_params.get('doctor_id')
        count = int(request.query_params.get('count'))
        query = request.query_params.get('query')

        queryset = Settlement.objects.all()  # Start with all records

        # Filter by doctor_id if provided
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id, points_settled_value__gt=0).exclude(product__name="Gift Product").order_by("-date_settled", "-time_settled")
            
            # Apply count-based slicing
            if queryset.count() >= count + 1:
                queryset_ = queryset[(count - 4):count]
            else:
                queryset_ = queryset[(count - 4):]  # Use the entire queryset if there are fewer than (count + 1) results
        
        # Apply the query filter if 'query' parameter is provided
        if query:
            queryset_ = queryset.filter(product__name__icontains=query)  # Adjust to the field you want to search

        # Debugging: Check the filtered queryset
        print(f"Filtered queryset for doctor_id {doctor_id}, query {query}: {queryset}")

        # Serialize the queryset and return the response
        serializer = SettlementSerializer(queryset_, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SettlementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class VSOSearchAPIView(APIView):

    def get(self, request):
        # Get filter parameters from the request query
        district = request.query_params.get('district')
        taluka = request.query_params.get('taluka')
        gavthan = request.query_params.get('gavthan')  # Optional
        name = request.query_params.get('name')  # Optional

        current_username = request.user
        # Step 2: Filter manager details based on username
        vso = VSOPersonalDetails.objects.get(email=current_username)

        
        # Start with all VSOs
        qs = DoctorPersonalDetails.objects.filter(vso=vso)

        # Apply filters based on the presence of query parameters
        if district:
            qs = qs.filter(district__icontains=district,vso=vso)  # Case-insensitive search
        if taluka:
            qs = qs.filter(taluka__icontains=taluka,vso=vso)
        if gavthan:
            qs = qs.filter(gavthan__icontains=gavthan,vso=vso)  # Assuming this is a field in your model
        if name:
            qs = qs.filter(name__icontains=name,vso=vso)

        # Serialize the filtered queryset
        serializer = DoctorSerializer(qs, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class TransactionDetailViewSet(viewsets.ModelViewSet):
    queryset = TransactionDetail.objects.all()
    serializer_class = TransactionDetailSerializer


class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer



class FreeSamplesByDoctorAPIViewSet(APIView):
    def get(self, request):
        # Retrieve doctor_id from query parameters
        doctor_id = request.query_params.get('doctor_id')
        count = int(request.query_params.get('count'))
        query = request.query_params.get('query')

        # Default value for queryset_
        queryset_ = None

        if doctor_id:
            # Filter products by doctor_id if provided
            queryset = Settlement.objects.filter(doctor_id=doctor_id, points_settled_value=0).order_by("-date_settled", "-time_settled")  # Adjust filter as necessary
            
            # Check if the queryset count is greater than the required count
            if queryset.count() >= count + 1:
                queryset_ = queryset[(count - 4):count]
            else:
                queryset_ = queryset[(count - 4):]  # Use the entire queryset if there are fewer than (count + 1) results
                
        # Apply the query filter if 'query' parameter is provided
        if query:
            queryset_ = queryset.filter(product__name__icontains=query)  # Adjust to the field you want to search

        # Debugging: Check the filtered queryset
        print(f"Filtered queryset for doctor_id {doctor_id}, query {query}: {queryset}")

        # Serialize the queryset and return the response
        serializer = SettlementSerializer(queryset_, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

       




class CreditsAPIView(APIView):
    
    def get(self, request):
        # Retrieve doctor_id from query parameters
        doctor_id = request.query_params.get('doctor_id')

        if doctor_id:
            # Filter products by doctor_id if provided
            queryset = DoctorCredit.objects.filter(doctor=doctor_id,repay_status=False).order_by("-date_issued")  # Adjust filter as necessary
        else:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)


        serializer = DoctorCreditSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

    


    def post(self, request, *args, **kwargs):
        try:
            # Debug: Log incoming request data
            print("Incoming data:", request.data)
            
            doctor_id = request.data.get('doctor_id')
            vso_id = request.data.get('vso_id')
            details = request.data.get('details', [])
            selectedList = request.data.get('selectedList', [])

            # Debug: Check required fields
            print("Doctor ID:", doctor_id)
            print("VSO ID:", vso_id)
            print("Details:", details)
            print("Selected List:", selectedList)

            if not doctor_id or not vso_id or not details or not selectedList:
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            # Debug: Log doctor and VSO fetching
            print("Fetching doctor and VSO details...")
            doctor = get_object_or_404(DoctorPersonalDetails, doctor_id=doctor_id)
            vso = get_object_or_404(VSOPersonalDetails, pk=vso_id)

            # Debug: Extract product IDs and check unsettled credits
            product_ids = [item['product'] for item in selectedList]
            print("Product IDs:", product_ids)

            unsettled_credits = DoctorCredit.objects.filter(
                doctor=doctor, 
                repay_status=False, 
                product__product_id__in=product_ids
            ).order_by('-date_issued')

            print("Unsettled Credits Count:", unsettled_credits.count())

            if not unsettled_credits.exists():
                return Response({"error": "No unsettled credits found."}, status=status.HTTP_404_NOT_FOUND)

            # Initialize total points and transactions
            total_points_repaid = 0
            transactions = []
            # remaining_points = sum(credit.outstanding_points for credit in unsettled_credits)
            # print("Remaining Points (Initial):", remaining_points)

            with transaction.atomic():
                for item in details:
                    product_name = item.get('product_name')
                    points_used = item.get('points_used', 0)
                    previous_points = item.get('previous_points', 0)
                

                    # Debug: Log product and points used
                    print("Processing Product:", product_name)
                    print("Points Used:", points_used)


                    if points_used <= 0:
                        return Response({"error": f"Invalid points for {product_name}."}, status=status.HTTP_400_BAD_REQUEST)

                    product = get_object_or_404(Product, name=product_name)

                    # Fetch the previous coupon
                    print(f"Fetching previous coupon for product {product_name}...")
                    previous_coupon = Coupon.objects.filter(
                        product=product, doctor=doctor, current_points__gt=0
                    ).order_by('-date_collected').first()

                    if not previous_coupon:
                        return Response({"error": f"No points for product {product_name}."}, status=status.HTTP_400_BAD_REQUEST)

                    print( f"current point: {previous_coupon.current_points}" )
                    
                    # Calculate current points
                    current_points = previous_points - points_used
                    print("Current Points After Deduction:", current_points)

                    if current_points < 0:
                        return Response({"error": f"Insufficient points for {product_name}."}, status=status.HTTP_400_BAD_REQUEST)

                    # Create transaction
                    print("Creating transaction...")
                    transaction_obj = Transaction.objects.create(
                        vso=vso, doctor=doctor, total_points_used=points_used, status='debits'
                    )
                    transactions.append(transaction_obj)

                    # Create coupon
                    print("Creating new coupon entry...")
                    new_coupon = Coupon.objects.create(
                        product=product, doctor=doctor, vso=vso,
                        coupon_points=points_used, current_points=current_points,
                        transaction=transaction_obj, status='redeemed'
                    )

                    # Process unsettled credits while deducting points
                    remaining_points = points_used* previous_coupon.product.coupon_value

                    # Process unsettled credits
                    for credit in unsettled_credits:
                        if remaining_points <= 0:
                            print("No remaining points to process.")
                            break

                        repay_points = min(credit.outstanding_points, remaining_points)
                        print("Repaying Points:", repay_points)

                        

                        repayment = CreditRepayment.objects.create(
                            credit=credit, transaction=transaction_obj
                        )
                        CreditRepaymentDetail.objects.create(
                            repayment=repayment, product=product, coupon=new_coupon,
                            points_repaid=repay_points
                        )

                        # Update credit fields
                        credit.repaid_points += repay_points
                        credit.outstanding_points -= repay_points
                        if(credit.outstanding_points == 0):
                            credit.repay_status = True
                            credit.date_repaid = transaction_obj.date_transaction
                        credit.save()

                        remaining_points -= repay_points
                        total_points_repaid += repay_points
                        print("Updated Remaining Points:", remaining_points)

                 # After processing, if remaining points are still positive, it means the repayment was not complete
                transaction_data = [{"transaction_id": txn.transaction_id, "points_used": txn.total_points_used} for txn in transactions]
            
                if remaining_points > 0:
                    partial_transaction_data = [
                        {
                            "transaction_id": txn.transaction_id,
                            "points_used": txn.total_points_used
                        } for txn in transactions
                    ]
                    return Response({
                        "message": "Partially repaid due to insufficient points.",
                        "total_points_repaid": total_points_repaid,
                        "remaining_points": remaining_points,
                        "transactions": partial_transaction_data
                    }, status=status.HTTP_200_OK)  

            # Prepare the response data
            transaction_data = [{"transaction_id": txn.transaction_id, "points_used": txn.total_points_used} for txn in transactions]
            return Response({
                "message": "Credits repaid successfully.",
                "total_points_repaid": total_points_repaid,
                "transactions": transaction_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class GiftSettledAPIViewSet(APIView):
    def get(self, request):
        # Retrieve doctor_id from query parameters
        doctor_id = request.query_params.get('doctor_id')
        count = int(request.query_params.get('count'))
        query = request.query_params.get('query')


        if doctor_id:
            # Filter products by doctor_id if provided
            queryset = Settlement.objects.filter(
                doctor_id=doctor_id, 
                points_settled_value__gt=0,
                product__name="Gift Product"
            ).order_by("-date_settled", "-time_settled")

            # Check if the queryset count is greater than the required count
            if queryset.count() >= count + 1:
                queryset_ = queryset[(count - 4):count]
            else:
                queryset_ = queryset[(count - 4):]  # Use the entire queryset if there are fewer than (count + 1) results
                

        # Apply the query filter if 'query' parameter is provided
        if query:
            queryset_ = queryset.filter(product__name__icontains=query)  # Adjust to the field you want to search

        # Debugging: Check the filtered queryset
        print(f"Filtered queryset for doctor_id {doctor_id}, query {query}: {queryset}")

        # Serialize the queryset and return the response
        serializer = SettlementSerializer(queryset_, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class RedeemProductByDoctorAPIView(APIView):
    
    def get(self, request):
        # Retrieve doctor_id, count, and query from query parameters
        doctor_id = request.query_params.get('doctor_id')
        count = int(request.query_params.get('count'))
        query = request.query_params.get('query')

        queryset = Settlement.objects.all()  # Start with all records

        # Filter by doctor_id if provided
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id, points_settled_value__gt=0).order_by("-date_settled", "-time_settled")
            
            # Apply count-based slicing
            if queryset.count() >= count + 1:
                queryset_ = queryset[(count - 4):count]
            else:
                queryset_ = queryset[(count - 4):]  # Use the entire queryset if there are fewer than (count + 1) results
        
        # Apply the query filter if 'query' parameter is provided
        if query:
            queryset_ = queryset.filter(product__name__icontains=query)  # Adjust to the field you want to search

        # Debugging: Check the filtered queryset
        print(f"Filtered queryset for doctor_id {doctor_id}, query {query}: {queryset}")

        # Serialize the queryset and return the response
        serializer = SettlementSerializer(queryset_, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CouponRedeemViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponRedeemSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        doctor_id = data.get('doctor')
        vso_id = data.get('vso')
        total_points_used_value = data.get('redeem_points_value', 0)
        total_points = data.get('redeem_points', 0)
        product_id_settled = data.get('product_id', 0)
        creditAllowed=data.get("creditAllowed", False)
        credit_points=data.get("creditPoints", 0)
        quantity=data.get("quantity", 0)
        status_=data.get("status", 0)
        details = data.get('details', [])
        total_coupon_points = 0
        total_coupon_value = 0.0

        #gifts products
        gift_name = data.get('Gift_name', "")
        gift_price = data.get('Gift_price', 0)

        

        

        # Retrieve the VSO and doctor instances
        try:
            vso = VSOPersonalDetails.objects.get(pk=vso_id)
            doctor = DoctorPersonalDetails.objects.get(pk=doctor_id,vso_id=vso.pk)
        except VSOPersonalDetails.DoesNotExist:
            return Response({"detail": "VSO not found."}, status=status.HTTP_404_NOT_FOUND)
        except DoctorPersonalDetails.DoesNotExist:
            return Response({"Error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        

        # Retrieve the product instance for the settlement record
        try:
            settled_product = Product.objects.get(pk=product_id_settled)
        except Product.DoesNotExist:
            return Response({"detail": f"Product with ID {product_id_settled} not found."}, status=status.HTTP_404_NOT_FOUND)

    

        

        # Filter coupons by doctor if doctor_id is provided, and exclude coupons with 0 points
        if doctor_id:
            # Subquery to get the latest coupon for each product
            latest_coupons = Coupon.objects.filter(
                product_id=OuterRef('product_id'),
                doctor_id=doctor_id,
                
            ).order_by('-date_collected', '-time_collected').values('coupon_id')[:1]

            # Filter coupons based on the most recent records per product
            coupons = (
                Coupon.objects.filter(coupon_id__in=Subquery(latest_coupons),current_points__gt=0)
                .annotate(
                    product_name=F('product__name'),
                    settlement_points=F('product__settlement_points'),
                    coupon_value=F('product__coupon_value'),
                    latest_transaction_date=F('date_collected'),
                    latest_transaction_time=F('time_collected'),
                )
                .order_by('-latest_transaction_date', '-latest_transaction_time')
            )
            serializer_data = CouponSerializer(coupons, many=True).data


            if(settled_product.name!="Gift Product"):
                    # Get the VSOProductStock record for the specific VSO and product
                    try:
                        vso_product_stock = VSOProductStock.objects.get(vso_id=vso_id, product_id=product_id_settled)

                    except:
                        return Response({"Error": f"Available products 0 and required products {quantity}"}, status=status.HTTP_400_BAD_REQUEST)

                    
                    # Check if there is enough stock to redeem
                    if vso_product_stock.current_stock < quantity:
                        return Response({"Error": f"Available products {vso_product_stock.current_stock} and required products {quantity}"}, status=status.HTTP_400_BAD_REQUEST)

            
                    # Update the stock (decrease by the redeemed quantity)
                    vso_product_stock.current_stock -= quantity
                    vso_product_stock.save()

                    # Log the stock transaction for redemption
                    StockTransaction.objects.create(
                        vso_product_stock=vso_product_stock,
                        used_quantity=quantity,
                        transaction_type=status_
                    )


            for coupon in serializer_data:
                coupon_points = int(coupon['current_points'])
                coupon_value = float(coupon["coupon_value"])
                total_coupon_points += coupon_points
                total_coupon_value += coupon_points * coupon_value

        
            transaction = Transaction.objects.create(
                        vso=vso,
                        doctor=doctor,
                        total_points_used=total_points,
                        status=status_
                )
            
            
            


            # Process each product in details
            for item in details:
                product_name = item.get('product_name')
                points_used = item.get('points_used', 0)
                quantity_redeemed = item.get('quantity_redeemed', 1)

                try:
                    product = Product.objects.get(name=product_name)
                except Product.DoesNotExist:
                    return Response({"detail": f"Product '{product_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
                

                
                # Calculate current points
                previous_coupons = Coupon.objects.filter(product=product, doctor=doctor,current_points__gt=0).order_by('-date_collected', '-time_collected').first()
                current_points = previous_coupons.current_points - points_used

                if current_points < 0:
                    return Response({
                        "error": f"Insufficient points for product '{product_name}'. Available: {current_points}, required: {points_used}."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            

                # Create a new coupon record
                new_coupon = Coupon.objects.create(
                    product=product,
                    doctor=doctor,
                    vso=vso,
                    coupon_points=points_used,
                    current_points=current_points,
                    transaction=transaction,
                    status=status_,
                )

                # Log the transaction detail
                TransactionDetail.objects.create(
                    transaction=transaction,
                    product=product,
                    previous_points=previous_coupons.current_points,
                    points_used=points_used,
                    quantity_redeemed=quantity_redeemed
                )

            
            
            # Create a settlement record with the product instance
            settlement_instance=Settlement.objects.create(
                transaction=transaction,
                doctor=doctor,
                points_settled_value=total_points_used_value,
                product=settled_product,
                credit_borrowed_points= credit_points if status_!="sampled" else 0,
                remaining_points_value=(total_coupon_value - total_points_used_value),
                vso=vso,
                quantity=quantity,
                product_type=status_,
            )


            if(settled_product.name=="Gift Product"):
                gifts=Gifts.objects.create(
                    gift_name=gift_name,
                    gift_price=gift_price,
                    settlement=settlement_instance
                )


        

            if creditAllowed and credit_points > 0:
                product = Product.objects.get(product_id=product_id_settled)
                credit = DoctorCredit.objects.create(
                            doctor=doctor,
                            product=product,
                            borrowed_points=abs(credit_points),
                            outstanding_points=abs(credit_points),

                )
                

            # Return a response with the transaction details
            return Response({
                "transactions": [CouponRedeemSerializer(transaction).data]
            }, status=status.HTTP_201_CREATED)
        



class VSOManagerAnalysisAPIView(APIView):

    def get(self, request):
        # Retrieve the manager_id from query parameters
        manager_id = request.query_params.get('manager_id')

        # Retrieve the date range and VSO ID from query parameters
        firstDate = request.query_params.get('firstDate')
        lastDate = request.query_params.get('lastDate')

        if not firstDate or not lastDate or not manager_id:
            return Response({"error": "Both firstDate, lastDate, and manager_id must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the date from string format to date objects
        first_date = datetime.strptime(firstDate, "%Y-%m-%d").date()
        last_date = datetime.strptime(lastDate, "%Y-%m-%d").date()

        # Fetch all VSOs under the given manager_id
        vsos = VSOPersonalDetails.objects.filter(manager_id=manager_id).values('vso_id', 'name', 'contact_no', 'email', 'district', 'taluka')

        if not vsos.exists():
            return Response({"error": "No VSOs found for the given manager ID."}, status=status.HTTP_404_NOT_FOUND)

        # Prepare response data
        vso_analysis_data = []

        for vso in vsos:
            # Fetch total coupon points collected by this VSO within the date range
            total_collected = Transaction.objects.filter(
                vso_id=vso['vso_id'],
                date_transaction__range=[first_date, last_date],
                status="collected"
            ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

            # Fetch total coupon points settled by this VSO within the date range
            total_settled = Transaction.objects.filter(
                vso_id=vso['vso_id'],
                date_transaction__range=[first_date, last_date],
                status="redeemed"
            ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

            # Fetch total coupon points collected by this VSO on a specific date (firstDate)
            total_collected_ondate = Transaction.objects.filter(
                vso_id=vso['vso_id'],
                date_transaction=first_date,
                status="collected"
            ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

            # Fetch total coupon points settled by this VSO on a specific date (firstDate)
            total_settled_ondate = Transaction.objects.filter(
                vso_id=vso['vso_id'],
                date_transaction=first_date,
                status="redeemed"
            ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

            # Fetch customer calls within the specified date range and count the days VSO connected with a doctor
            customer_calls = Transaction.objects.filter(
                vso_id=vso['vso_id'],  # Replace with the actual VSO ID you're querying
                date_transaction__range=(first_date, last_date)
            ).values('doctor_id', 'date_transaction') \
            .distinct()  # Only consider distinct days of interaction

            call_days = customer_calls.values('doctor_id').annotate(
                total_call_days=Count('date_transaction', distinct=True)
            )
            

            # Fetch detailed products for collected points within the date range
            collected_detailed_products = (
                TransactionDetail.objects.filter(
                    transaction__vso_id=vso['vso_id'],
                    transaction__date_transaction__range=[first_date, last_date],
                    transaction__status='collected'
                )
                .select_related('product')
                .values('product__name', 'product__coupon_value')
                .annotate(
                    quantity_collected=Sum('quantity_redeemed'),
                    total_collected_value=Sum('points_used')
                )
            )

            # Fetch detailed products for redeemed points within the date range
            redeemed_detailed_products = (
                TransactionDetail.objects.filter(
                    transaction__vso_id=vso['vso_id'],
                    transaction__date_transaction__range=[first_date, last_date],
                    transaction__status='redeemed'
                )
                .select_related('product')
                .values('product__name', 'product__coupon_value')
                .annotate(
                    quantity_redeemed=Sum('quantity_redeemed'),
                    total_redeemed_value=Sum('points_used')
                )
            )

            # Prepare data for collected products
            collected_products_data = [
                {
                    'product_name': product['product__name'],
                    'quantity_collected': product['quantity_collected'],
                    'total_collected_value': product['total_collected_value'] * product['product__coupon_value']
                }
                for product in collected_detailed_products
            ]

            # Prepare data for redeemed products
            redeemed_products_data = [
                {
                    'product_name': product['product__name'],
                    'quantity_redeemed': product['quantity_redeemed'],
                    'total_redeemed_value': product['total_redeemed_value'] * product['product__coupon_value']
                }
                for product in redeemed_detailed_products
            ]

            # Prepare customer call data
            customer_call_data = [
                {
                    'doctor_name': DoctorPersonalDetails.objects.get(doctor_id=call['doctor_id']).name,
                    'call_count': call['total_call_days']
                }
                for call in call_days
            ]

            # Calculate bonus points based on collected products
            bonus_points = (
                TransactionDetail.objects.filter(
                    transaction__vso_id=vso['vso_id'],
                    transaction__status="collected",  # Change status to 'collected'
                    transaction__date_transaction__range=[first_date, last_date],
                )
                .annotate(bonus=F('points_used') * F('product__bonus_points'))  # Use quantity_collected
                .aggregate(total_bonus=Sum('bonus'))['total_bonus'] or 0  # Sum the calculated bonuses
            )


            current_bonus_points=(
                BonusRecords.objects.filter(
                    manager_id=manager_id
                ).values("current_bonus_points")
            )


            # Add VSO data to the response
            vso_analysis_data.append({
                "name": vso['name'],
                "contact_no": vso['contact_no'],
                "email": vso['email'],
                "district": vso['district'],
                "taluka": vso['taluka'],
                "total_collected": total_collected,
                "total_settled": total_settled,
                "total_collected_ondate": total_collected_ondate,
                "total_settled_ondate": total_settled_ondate,
                "bonus_points": bonus_points,
                "current_bonus_points": current_bonus_points[0]["current_bonus_points"],
                "customer_calls": customer_call_data,
                "collected_detailed_products": collected_products_data,
                "redeemed_detailed_products": redeemed_products_data,
            })

        # Return the final response
        return Response(vso_analysis_data, status=status.HTTP_200_OK)




class VSOAnalysisAPIView(APIView):

    def get(self, request):
        # Retrieve the first date, last date, and VSO ID from query parameters
        first_date = request.query_params.get('firstDate')
        last_date = request.query_params.get('lastDate')
        vso_id = request.query_params.get('vso_id')

        if not first_date or not last_date or not vso_id:
            return Response({"error": "firstDate, lastDate, and vso_id must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse firstDate
            first_date = datetime.strptime(first_date, "%Y-%m-%d").date()

            # Parse lastDate to handle both date-only and datetime strings
            try:
                last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
            except ValueError:
                last_date = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S.%f").date()
        except ValueError as e:
            return Response({"error": f"Invalid date format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Total CP collected from TransactionDetail
        total_collected = TransactionDetail.objects.filter(
            transaction__vso_id=vso_id,
            transaction__date_transaction__range=(first_date, last_date),
            transaction__status='collected'
        ).aggregate(total_collected=Sum('points_used'))['total_collected'] or 0

        # Total CP settled from TransactionDetail
        total_settled = TransactionDetail.objects.filter(
            transaction__vso_id=vso_id,
            transaction__date_transaction__range=(first_date, last_date),
            transaction__status='redeemed'
        ).aggregate(total_settled=Sum('points_used'))['total_settled'] or 0


        # Fetch customer calls within the date range
        total_settled_ondate = Transaction.objects.filter(
                vso_id=vso_id,
                date_transaction=first_date,
                status="redeemed"
        ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

        # Fetch customer calls within the specified date range and count the days VSO connected with a doctor
        customer_calls = Transaction.objects.filter(
                vso_id=vso_id,  # Replace with the actual VSO ID you're querying
                date_transaction__range=(first_date, last_date)
            ).values('doctor_id', 'date_transaction').distinct()  # Only consider distinct days of interaction

        call_days = customer_calls.values('doctor_id').annotate(
                total_call_days=Count('date_transaction',distinct=True)
        )
       

        # Fetch detailed products for collected points within the date range
        collected_detailed_products = (
            TransactionDetail.objects.filter(
                transaction__vso_id=vso_id,
                transaction__date_transaction__range=(first_date, last_date),
                transaction__status='collected'
            )
            .select_related('product')
            .values('product__name', 'product__coupon_value')
            .annotate(
                quantity_collected=Sum('points_used')  # Assuming points_used is the quantity collected
            )
        )

        # Calculate total_collected_value by multiplying quantity_collected with coupon_value
        collected_detailed_products = [
            {
                **product,
                'total_collected_value': product['quantity_collected'] * product['product__coupon_value']
            }
            for product in collected_detailed_products
        ]

        # Fetch detailed products for redeemed points within the date range
        redeemed_detailed_products = (
            TransactionDetail.objects.filter(
                transaction__vso_id=vso_id,
                transaction__date_transaction__range=(first_date, last_date),
                transaction__status='redeemed'
            )
            .select_related('product')
            .values('product__name', 'product__coupon_value')
            .annotate(
                quantity_redeemed=Sum('points_used')  # Assuming points_used is the quantity redeemed
            )
        )

        # Calculate total_redeemed_value by multiplying quantity_redeemed with coupon_value
        redeemed_detailed_products = [
            {
                **product,
                'total_redeemed_value': product['quantity_redeemed'] * product['product__coupon_value']
            }
            for product in redeemed_detailed_products
        ]

        # Prepare data for collected products
        collected_products_data = [
            {
                'product_name': product['product__name'],
                'quantity_collected': product['quantity_collected'],
                'total_collected_value': product['total_collected_value']
            }
            for product in collected_detailed_products
        ]

        # Prepare data for redeemed products
        redeemed_products_data = [
            {
                'product_name': product['product__name'],
                'quantity_redeemed': product['quantity_redeemed'],
                'total_redeemed_value': product['total_redeemed_value']
            }
            for product in redeemed_detailed_products
        ]


        # Fetch total coupon points collected by this VSO ondate
        total_collected_ondate = Transaction.objects.filter(
                vso_id=vso_id,
                date_transaction=first_date,
                status="collected"
        ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

        # Fetch total coupon points settled by this VSO ondate
        total_settled_ondate = Transaction.objects.filter(
                vso_id=vso_id,
                date_transaction=first_date,
                status="redeemed"
        ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

          # Fetch detailed products for collected points onday
        collected_detailed_products_ondate = (
            TransactionDetail.objects.filter(
                transaction__vso_id=vso_id,
                transaction__date_transaction=first_date,
                transaction__status='collected'  # Add the filter for 'collected' status
            )
            .select_related('product')  # Optimize query by joining with Product
            .values('product__name', 'product__coupon_value')  # Get product name and coupon value
            .annotate(
                quantity_collected=Sum('quantity_redeemed'),  # Sum of quantity collected
                total_collected_value=Sum('points_used')  # Sum of points used, assuming this represents the coupon value
            )
        )

        # Fetch detailed products for redeemed points
        redeemed_detailed_products_ondate = (
            TransactionDetail.objects.filter(
                transaction__vso_id=vso_id,
                transaction__date_transaction=first_date,
                transaction__status='redeemed'  # Add the filter for 'redeemed' status
            )
            .select_related('product')  # Optimize query by joining with Product
            .values('product__name', 'product__coupon_value')  # Get product name and coupon value
            .annotate(
                quantity_redeemed=Sum('quantity_redeemed'),  # Sum of quantity redeemed
                total_redeemed_value=Sum('points_used')  # Sum of points used, assuming this represents the coupon value
            )
        )


        # Prepare data for collected products
        collected_products_data_ondate = [
            {
                'product_name': product['product__name'],
                'quantity_collected': product['total_collected_value'],
                'total_collected_value': product['total_collected_value']*product['product__coupon_value']
            }
            for product in collected_detailed_products_ondate
        ]

        # Prepare data for redeemed products
        redeemed_products_data_ondate = [
            {
                'product_name': product['product__name'],
                'quantity_redeemed': product['total_redeemed_value'],
                'total_redeemed_value': product['total_redeemed_value']*product['product__coupon_value']
            }
            for product in redeemed_detailed_products_ondate
        ]


        # Prepare the response data
        analysis_data = {
            "total_collected": total_collected,
            "total_settled": total_settled,
            "total_collected_ondate": total_collected_ondate,
            "total_settled_ondate": total_settled_ondate,
            "customer_calls": [
                {
                    'doctor_name': DoctorPersonalDetails.objects.get(doctor_id=call['doctor_id']).name,
                    'call_count': call['total_call_days']
                }
                for call in call_days
            ],
             "collected_detailed_products_ondate": collected_products_data_ondate,
            "redeemed_detailed_products_ondate": redeemed_products_data_ondate,
            "collected_detailed_products": collected_products_data,
            "redeemed_detailed_products": redeemed_products_data,
        }

        return Response(analysis_data, status=status.HTTP_200_OK)



class VSOMonthPerformanceAPIView(APIView):
        
    def get(self, request):
        # Retrieve the current date and month
        today = timezone.now()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timezone.timedelta(days=31)).replace(day=1)

        # Retrieve VSO ID from query parameters
        vso_id = request.query_params.get('vso_id')
        if not vso_id:
            return Response({"error": "vso_id must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total coupon points collected for the current month
        total_collected = Transaction.objects.filter(
            vso_id=vso_id,
            date_transaction__gte=start_of_month,
            date_transaction__lt=end_of_month,
            status="collected"
        ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

        # Calculate total coupon points settled for the current month
        total_settled = Transaction.objects.filter(
            vso_id=vso_id,
            date_transaction__gte=start_of_month,
            date_transaction__lt=end_of_month,
            status="redeemed"
        ).aggregate(Sum('total_points_used'))['total_points_used__sum'] or 0

        # Count total doctors under the VSO
        total_doctors = DoctorPersonalDetails.objects.filter(vso_id=vso_id).count()

        # Count total customer calls for the current month
        customer_calls = Transaction.objects.filter(
            vso_id=vso_id,
            date_transaction__gte=start_of_month,
            date_transaction__lt=end_of_month
        ).values('doctor_id').distinct().count()  # Count unique doctors called

        # Prepare the response data
        analysis_data = {
            "total_collected": total_collected,
            "total_settled": total_settled,
            "total_doctors": total_doctors,
            "total_customer_calls": customer_calls,
        }

        return Response(analysis_data, status=status.HTTP_200_OK)



class DoctorLastUpdate(APIView):
    
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')

        # Get the latest coupon entry date for the doctor
        latest_coupon = Coupon.objects.filter(doctor_id=doctor_id).order_by('-date_collected').first()
        if not latest_coupon:
            return Response({'error': 'No coupon data found for this doctor'}, status=404)

        latest_date = latest_coupon.date_collected


        
        # Find the previous transaction or settlement date before the latest date
        previous_date = Transaction.objects.filter(
            doctor_id=doctor_id,
            date_transaction__lt=latest_date
        ).order_by('-date_transaction').values_list('date_transaction', flat=True).first()

        

        # Calculate collected points cost for the latest date
        collected_points_cost = TransactionDetail.objects.filter(
            transaction__date_transaction=latest_date,
            transaction__status="collected",
            transaction__doctor_id=latest_coupon.doctor
        ).annotate(
            product_cost=F("transaction__total_points_used") * F("product__coupon_value")
        ).aggregate(total_collected_cost=Sum("product_cost"))['total_collected_cost'] or 0

        # Calculate redeemed points cost for the latest date
        redeemed_points_cost = Settlement.objects.filter(
            doctor_id=doctor_id,
            date_settled=latest_date
        ).aggregate(total_redeemed_cost=Sum("points_settled_value"))['total_redeemed_cost'] or 0

        # Calculate total points repaid for a specific doctor on a particular date
        total_repaid_points = CreditRepaymentDetail.objects.filter(
            repayment__credit__doctor=doctor_id,  # Filter by doctor ID through the repayment relationship
            repayment__date_repaid=latest_date  # Filter by settlement date through the repayment relationship
        ).aggregate(total_points_repaid=Sum('points_repaid'))['total_points_repaid'] or 0

        # Filter DoctorCredit entries for the given doctor where repay_status is False
        queryset = DoctorCredit.objects.filter(doctor=doctor_id, repay_status=False).order_by("-date_issued")

        # Calculate total credit
        total_credit = queryset.aggregate(total_credit=Sum('outstanding_points'))['total_credit'] or 0








        # Initialize previous remaining points
        total_coupons_value = 0
        if previous_date:
            

            latest_coupons_subquery = Coupon.objects.filter(
                    product_id=OuterRef('product_id'),
                    doctor_id=doctor_id,
                    date_collected__lte=previous_date,  # Filter for the specific date
                ).order_by('-date_collected', '-time_collected').values('coupon_id')[:1]
            
                
                # Query to filter latest coupons and calculate the total coupon value
            total_coupons_value = Coupon.objects.filter(
                    coupon_id__in=Subquery(latest_coupons_subquery),
                    current_points__gt=0,
                    date_collected__lte=previous_date,
                ).aggregate(
                    total_value=Sum(F('current_points') * F('product__coupon_value'))
                )['total_value'] or 0
                
        # Prepare response data
        response_data = {
            'vso_id': latest_coupon.vso.vso_id,
            'vso_name': latest_coupon.vso.name,
            'vso_contact': latest_coupon.vso.contact_no,
            'total_credit':total_credit,
            
            'latest_coupon': {
                'date_collected': latest_date,
                'coupon_points': latest_coupon.coupon_points,
            },
            'transaction_summary': {
                'total_collected_points_cost': collected_points_cost,
                'total_redeemed_points_cost': redeemed_points_cost + total_repaid_points,
                'total_coupon_points': total_coupons_value  # Returning previous remaining points here
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
    


class DoctorLastVisitSettlements(APIView):

    def get(self, request):
        # Retrieve query parameters
        doctor_id = request.query_params.get('doctor_id')
        product_type = request.query_params.get('type')  # Expected values: "settled" or "sampled"

        # Validate doctor_id
        if not doctor_id:
            return Response(
                {"error": "doctor_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate product_type
        if product_type not in ["redeemed", "sampled"]:
            return Response(
                {"error": "Invalid type parameter. Expected 'redeemed' or 'sampled'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the last settlement for the doctor
            last_settlement = Settlement.objects.filter(
                doctor_id=doctor_id
            ).order_by("-date_settled", "-time_settled").first()

            # If no settlement is found, return a not-found response
            if not last_settlement:
                return Response(
                    {"message": "No settlements found for the doctor."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Filter products based on type (settled or sampled)
            transaction_details = Settlement.objects.filter(
                doctor=doctor_id,
                date_settled=last_settlement.date_settled,
                transaction__status=product_type  # Use product_type here
            ).select_related('product').values(
                'product__name', 
                'product__coupon_value'
            ).annotate(
                quantity_collected=Sum('quantity'),
                total_collected_value=Sum('points_settled_value')
            )


            # Prepare product data from the filtered transaction details
            product_data = [
                {
                    "product_name": td['product__name'],
                    "quantity_used": int(td['quantity_collected']),
                }
                for td in transaction_details
            ]


            

            return Response(product_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class SettledStockAPIView(APIView):
    """
    API to get the settled stock (redeemed stock) for a specific VSO and product, including working stock.
    """

    def get(self, request, *args, **kwargs):
        vso_id = self.request.query_params.get('vso_id')

        if not vso_id:
            return Response({"error": "vso_id is required as a query parameter"}, status=400)

        # Get all VSOProductStock records for the specific VSO
        vso_product_stocks = VSOProductStock.objects.filter(vso_id=vso_id)

        if not vso_product_stocks.exists():
            return Response({"error": "No product stocks found for the given VSO"}, status=404)

        data = []
        for vso_product_stock in vso_product_stocks:
            # Start with the current stock from VSOProductStock
            current_stock = vso_product_stock.current_stock

            # Get all transactions for this product stock ordered by date (descending)
            transactions = StockTransaction.objects.filter(
                vso_product_stock=vso_product_stock
            ).order_by('-transaction_date')

            # Initialize stock breakdown variables
            settled_stock = 0
            sampled_stock = 0
            collected_stock = 0

            # Reverse sum the transactions
            for transaction in transactions:
                if transaction.transaction_type == 'redeemed':
                    settled_stock += transaction.used_quantity
                elif transaction.transaction_type == 'sampled':
                    sampled_stock += transaction.used_quantity
                elif transaction.transaction_type == 'collected':
                    collected_stock += transaction.used_quantity

                # Break the loop if the total reverse-summed stock matches the current stock
                if collected_stock - (settled_stock + sampled_stock) == current_stock:
                    break

            # Add the details to the response data
            data.append({
                "product_name": vso_product_stock.product.name,
                "current_stock": current_stock,
                "settled_stock": settled_stock,
                "sampled_stock": sampled_stock,
                "collected_stock": collected_stock,
                "remaining_stock": current_stock - (settled_stock + sampled_stock),
            })

        return Response(data, status=status.HTTP_200_OK)




class CurrentStockAPIView(APIView):
    """
    API to get the current stock for a specific VSO and product, including product name and image.
    """

    def get(self, request, *args, **kwargs):
        vso_id = self.request.query_params.get('vso_id')

        if not vso_id:
            return Response({"error": "vso_id is required as a query parameter"}, status=400)

        # Get all VSOProductStock records for the specific VSO
        vso_product_stocks = VSOProductStock.objects.filter(vso_id=vso_id)

        if not vso_product_stocks.exists():
            return Response({"error": "No product stocks found for the given VSO"}, status=404)

        data = []
        for vso_product_stock in vso_product_stocks:
            data.append({
                "product_name": vso_product_stock.product.name,
                "current_stock": vso_product_stock.current_stock,
            })

        return Response(data, status=status.HTTP_200_OK)
    




class BonusSettlementView(APIView):
    """
    API to retrieve bonus settlement data.
    """

    def get(self, request):
        # Retrieve doctor_id, count, and query from query parameters
        manager_id = request.query_params.get('manager_id')
        count = int(request.query_params.get('count', 4))  # Default count to 10 if not provided
        query = request.query_params.get('query', '')

        queryset = BonusSettlement.objects.all()  # Start with all records

        # Filter by doctor_id if provided
        if manager_id:
            queryset = queryset.filter(manager_id=manager_id).order_by("-created_at")

            # Apply count-based slicing
            if queryset.count() >= count + 1:
                queryset_ = queryset[(count - 4):count]  # Adjust the slicing if there are enough records
            else:
                queryset_ = queryset[(count - 4):]  # Use the entire queryset if there are fewer than (count + 1) results
        
        else:
            queryset_ = queryset  # If no doctor_id, return the entire queryset

        # Apply the query filter if 'query' parameter is provided
        if query:
            queryset_ = queryset_.filter(settlement_title__icontains=query)  # Filter by settlement_title or any other relevant field

        # Debugging: Check the filtered queryset
        print(f"Filtered queryset for doctor_id {manager_id}, query {query}: {queryset_}")

        # Serialize the queryset and return the response
        serializer = BonusSettlementSerializer(queryset_, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


