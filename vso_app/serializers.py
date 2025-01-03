from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model
from .models import BonusSettlement, CreditRepayment, DoctorCredit, Gifts, ManagerPersonalDetails,  TransactionDetail,  VSOPersonalDetails, DoctorPersonalDetails, Product, Coupon,  Transaction, Settlement, VSOProductStock



class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField( trim_whitespace=False)

    

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            
            user = UserModel.objects.get(username=username)
            
        except UserModel.DoesNotExist:
            return None
        if user.password==password:
            return user
        return None




    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = self.authenticate(request=self.context.get('request'), username=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    


class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField( trim_whitespace=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user
    

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPersonalDetails
        fields = '__all__'

class VSOSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = VSOPersonalDetails
        fields = '__all__'

    def create(self, validated_data):
        # Extract the email string from validated data
        email_username = validated_data.get('email')
        
        # Retrieve the User instance based on the username (email)
        try:
            user = User.objects.get(username=email_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        # Replace the email field with the User instance in validated_data
        validated_data['email'] = user
        
        # Create the VSOPersonalDetails instance with the modified validated_data
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Extract the email string from validated data
        email_username = validated_data.get('email', None)

        # If email is provided, update it with the corresponding User instance
        if email_username:
            try:
                user = User.objects.get(username=email_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "User with this email does not exist."})
            validated_data['email'] = user

        # Call the parent class's update method to handle the actual update
        return super().update(instance, validated_data)


class DoctorSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = DoctorPersonalDetails
        fields = '__all__'

    def create(self, validated_data):
        # Extract the email string from validated data
        email_username = validated_data.get('email')
        
        # Retrieve the User instance based on the username (email)
        try:
            user = User.objects.get(username=email_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        # Replace the email field with the User instance in validated_data
        validated_data['email'] = user
        
        # Create the VSOPersonalDetails instance with the modified validated_data
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Extract the email string from validated data
        email_username = validated_data.get('email', None)

        # If email is provided, update it with the corresponding User instance
        if email_username:
            try:
                user = User.objects.get(username=email_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "User with this email does not exist."})
            validated_data['email'] = user

        # Call the parent class's update method to handle the actual update
        return super().update(instance, validated_data)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'market_price', 'settlement_points', "coupon_value",'image']



class CouponSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    settlement_points = serializers.DecimalField(source='product.settlement_points', max_digits=10, decimal_places=2, read_only=True)
    coupon_value = serializers.DecimalField(source='product.coupon_value', max_digits=10, decimal_places=2, read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    
    class Meta:
        model = Coupon
        fields = ['coupon_id', 'current_points', 'date_collected', "time_collected",'status', 'vso', 'doctor', 'product_id', 'product_name', 'settlement_points','coupon_value']



class DoctorCreditSerializer(serializers.ModelSerializer):
   
    product_name = serializers.CharField(source='product.name', read_only=True)  # Adding product name for convenience

    class Meta:
        model = DoctorCredit
        fields = [
            'id',               # Unique identifier for the credit
            'doctor',           # Foreign key to DoctorPersonalDetails
            'product',          # Foreign key to Product
            'borrowed_points',  # Points borrowed by the doctor
            'repaid_points',    # Points repaid by the doctor
            'repay_status',     # Status indicating whether the credit is repaid
            'date_issued',      # Date the credit was issued
            'date_repaid',      # Date the credit was fully repaid (nullable)
            'product_name',     # Convenience field to show the product's name
        ]
        read_only_fields = [ 'product_name', 'id']  # Prevent modification of convenience fields


class CouponSerializerPOST(serializers.ModelSerializer):
    
    class Meta:
        model = Coupon
        fields = ['coupon_id', 'current_points', 'status', 'vso', 'doctor','doctor_id', 'product']




class TransactionDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    coupon_value = serializers.DecimalField(source='product.coupon_value', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = TransactionDetail
        fields = ['product', 'previous_points', 'points_used', 'quantity_redeemed','product_name',"coupon_value"]

class TransactionSerializer(serializers.ModelSerializer):
    details = TransactionDetailSerializer(many=True)
    

    class Meta:
        model = Transaction
        fields = ['transaction_id','vso', 'doctor', 'total_points_used', "status","date_transaction",'time_transaction', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = Transaction.objects.create(**validated_data)
        for detail in details_data:
            TransactionDetail.objects.create(transaction=transaction, **detail)
        return transaction

class CouponRedeemSerializer(serializers.ModelSerializer):
    details = TransactionDetailSerializer(many=True)

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'vso',              # Foreign key to the VSO model
            'doctor',           # Foreign key to the Doctor model
            'total_points_used',
            'status',
            'details'
        ]

    def create(self, validated_data):
        # Pop out the nested `details` data for handling separately
        details_data = validated_data.pop('details')
        transaction = Transaction.objects.create(**validated_data)

        # Create TransactionDetail entries based on the details provided
        for detail in details_data:
            TransactionDetail.objects.create(transaction=transaction, **detail)

        return transaction


class SettlementSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Expecting a single product
    
    class Meta:
        model = Settlement
        fields = '__all__'


class ManagerPersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPersonalDetails
        fields = '__all__'


class VSOPersonalDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = VSOPersonalDetails
        fields = '__all__'

    def get_email(self, instance):
        # Return the username (email) of the related User instance
        return instance.email.username if instance.email else None

class DoctorPersonalDetailsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = DoctorPersonalDetails
        fields = '__all__'
    
    def get_email(self, instance):
        # Return the username (email) of the related User instance
        return instance.email.username if instance.email else None


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'








class CreditRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRepayment
        fields = '__all__'


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gifts
        fields = '__all__'


class BonusSettlementSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    bonus_record_title = serializers.CharField(source='bonusRecords.title', read_only=True)

    class Meta:
        model = BonusSettlement
        fields = [
            'id',
            'manager_name',
            'bonus_record_title',
            'bonus_points_used',
            'remaining_bonus_points',
            'settlement_title',
            'settlement_description',
            'created_at',
        ]