from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from manager_app.models import ManagerPersonalDetails
from django.db.models import Sum

# 2. VSO Table (Sales Voice Officers)
class VSOPersonalDetails(models.Model):
    vso_id = models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15,unique=True)
    email = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    dob = models.DateField(null=True,)
    gender = models.CharField(max_length=6,null=True, blank=True)  # Gender field
    manager = models.ForeignKey(ManagerPersonalDetails, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vsos/', null=True, blank=True)  # Add image field

    def __str__(self):
        return f"{self.name}-{self.vso_id}"




class DoctorPersonalDetails(models.Model):
    doctor_id = models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    email = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=15,unique=True)
    dob = models.DateField(null=True,)
    gender = models.CharField(max_length=6,null=True, blank=True)  # Gender field
    vso = models.ForeignKey(VSOPersonalDetails, on_delete=models.SET_NULL, null=True)  # Add VSO reference
    image = models.ImageField(upload_to='doctors/', null=True, blank=True)  # Add image field

    def __str__(self):
        return self.doctor_id
    

# 4. Product Table
class Product(models.Model):
    product_type=models.CharField(max_length=100,choices=[ ('redeemed', 'Redeemed'),('sampled', 'Sampled')])
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="No description available")
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    settlement_points = models.IntegerField(default=0)
    coupon_value = models.IntegerField(default=0)
    bonus_points =  models.IntegerField(default=0)
    sample_points =  models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)  # Assuming you want to upload an image

    def __str__(self):
        return f"{self.name}-{self.product_id}"







# 7. Transaction Table
class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    vso = models.ForeignKey(VSOPersonalDetails, on_delete=models.CASCADE)  # Ensure this model is defined and used correctly
    doctor = models.ForeignKey(DoctorPersonalDetails, on_delete=models.CASCADE)  # Ensure this model is defined and used correctly
    total_points_used = models.IntegerField()
    date_transaction = models.DateField(auto_now=True)  # Automatically sets the date when the transaction is created
    time_transaction = models.TimeField(auto_now_add=True)  # Time when the transaction occurred
    status = models.CharField(max_length=20, choices=[('collected', 'Collected'), ('redeemed', 'Redeemed'),('sampled', 'Sampled'),("credits","Credits"),("debits","Debits"),])


    def __str__(self):
        return f"Transaction {self.transaction_id}-{self.doctor}-{self.status}-{self.date_transaction}"


#8. Transaction Details
class TransactionDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)  # Unique ID for each transaction detail
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='details')  # Foreign key to Transaction table
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    previous_points = models.IntegerField()  # Points before redemption
    points_used = models.IntegerField()  # Points used for this specific product
    quantity_redeemed = models.IntegerField(default=1)  # Quantity of product redeemed

    class Meta:
        db_table = 'transaction_detail'  # Specify the table name in the database
        unique_together = ('transaction', 'product')  # Ensure a product can only be redeemed once per transaction

    def __str__(self):
        return f"{self.quantity_redeemed} of {self.product.name} {self.transaction.status} for {self.points_used} points"




# 5. Coupon Table
class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    vso = models.ForeignKey(VSOPersonalDetails, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorPersonalDetails, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coupon_points = models.IntegerField()
    current_points = models.IntegerField(default=0)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date_collected = models.DateField(auto_now=True)
    time_collected = models.TimeField(auto_now_add=True,blank=True)  
    status = models.CharField(max_length=20, choices=[('collected', 'Collected'), ('redeemed', 'Redeemed')])

    def __str__(self):
        return f"Coupon {self.coupon_id}"
    



# 9. Settlement Table
class Settlement(models.Model):
    settlement_id = models.AutoField(primary_key=True)
    vso = models.ForeignKey(VSOPersonalDetails, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorPersonalDetails, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    points_settled_value = models.IntegerField()
    credit_borrowed_points = models.IntegerField()
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    remaining_points_value = models.IntegerField()
    quantity = models.IntegerField()
    product_type=models.CharField(max_length=100,choices=[('redeemed', 'Redeemed'), ('sampled', 'Sampled')])
    date_settled = models.DateField(auto_now_add=True)
    time_settled = models.TimeField(auto_now_add=True,blank=True)  
    

    def __str__(self):
        return f"Settlement {self.settlement_id} on {self.date_settled}"


class DoctorCredit(models.Model):
    doctor = models.ForeignKey(DoctorPersonalDetails, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    borrowed_points = models.IntegerField()
    repaid_points = models.IntegerField(default=0)  # Tracks total repaid points for this credit
    repay_status = models.BooleanField(default=False)  # Indicates if the credit is fully repaid
    date_issued = models.DateField(auto_now_add=True)
    date_repaid = models.DateField(null=True, blank=True)  # Optional, updated when fully repaid
    outstanding_points=models.IntegerField(default=0)

    def __str__(self):
        return f"Doctor: {self.doctor.name}, Product: {self.product.name}, Borrowed: {self.borrowed_points}"

    

    @classmethod
    def borrow_limit(cls, doctor):
        """Checks the total borrowed points for the doctor to ensure it doesn't exceed 400."""
        total_borrowed = cls.objects.filter(doctor=doctor, repay_status=False).aggregate(total=Sum('borrowed_points'))['total'] or 0
        return total_borrowed

    def clean(self):
        """Ensure the doctor does not borrow more than the maximum allowed (400 points)."""
        max_borrow_limit = 400
        if self.borrowed_points + DoctorCredit.borrow_limit(self.doctor) > max_borrow_limit:
            raise ValidationError(f"Doctor can only borrow a maximum of {max_borrow_limit} points. Current total borrowed exceeds this limit.")

    
class CreditRepayment(models.Model):
    credit = models.ForeignKey(DoctorCredit, on_delete=models.CASCADE)  # The credit being repaid
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)  # Links to the settlement for this repayment
    date_repaid = models.DateField(auto_now_add=True)  # Date when the repayment occurred

    def __str__(self):
        return f"Credit ID: {self.credit.id}, Date Repaid: {self.date_repaid}"




class CreditRepaymentDetail(models.Model):
    repayment = models.ForeignKey(CreditRepayment, on_delete=models.CASCADE)  # Links to the repayment record
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # The product contributing to this repayment
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)  # Optional, tracks specific coupon
    points_repaid = models.IntegerField()  # Number of points repaid using this product

    def __str__(self):
        return f"Repayment ID: {self.repayment.id}, Product: {self.product.name}, Points Repaid: {self.points_repaid}"


class VSOProductStock(models.Model):
    vso = models.ForeignKey('VSOPersonalDetails', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    current_stock = models.IntegerField(default=0)  # Current stock assigned to the VSO
    
    class Meta:
        unique_together = ('vso', 'product')  # Enforce uniqueness of VSO and Product


    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new record

        if not is_new:
            # If the record exists, get the original instance to compare stocks
            original = VSOProductStock.objects.get(pk=self.pk)
            stock_difference = self.current_stock - original.current_stock

            # Save the current instance before creating transactions
            super().save(*args, **kwargs)

            if stock_difference > 0:  # Stock increased
                StockTransaction.objects.create(
                    vso_product_stock=self,
                    used_quantity=stock_difference,
                    transaction_type='collected',
                )
            
        else:
            # For new records, save first, then create a "collected" transaction
            super().save(*args, **kwargs)
            if self.current_stock > 0:
                StockTransaction.objects.create(
                    vso_product_stock=self,
                    used_quantity=self.current_stock,
                    transaction_type='collected',
                )

        # Update previous_quantity after processing
        self.previous_quantity = self.current_stock
        super().save(*args, **kwargs)  # Save again to update fields
        
    def __str__(self):
        return f"{self.vso} - {self.product} - Current Stock: {self.current_stock}"


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('collected', 'Collected'),  # Adding stock
        ('redeemed', 'Redeemed'),    # Using stock
        ('sampled', 'Sampled'), 
    ]

    vso_product_stock = models.ForeignKey('VSOProductStock', on_delete=models.CASCADE, related_name='transactions')
    used_quantity = models.IntegerField(default=0)  # Quantity involved in this transaction
    transaction_date = models.DateTimeField(auto_now_add=True)  # Date of transaction
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='redeemed')

    
    def __str__(self):
        return f"{self.transaction_type.capitalize()} Transaction: {self.used_quantity} of {self.vso_product_stock.product.name} by {self.vso_product_stock.vso}"




class Gifts(models.Model):
    gift_name = models.CharField(max_length=100)  # The gift name
    gift_price = models.IntegerField()  # The gift price
    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE)  # settlement details
    
    def __str__(self):
            return f"Gift Name: {self.gift_name}, Gift Price: {self.gift_price} , Date: {self.settlement.date_settled}"

class BonusRecords(models.Model):
    manager = models.ForeignKey(
        ManagerPersonalDetails, on_delete=models.CASCADE, related_name='bonus_records'
    )
    current_bonus_points = models.PositiveIntegerField(default=0)  # Tracks the available bonus points
    last_updated_at = models.DateTimeField(auto_now=True)  # Tracks when the last update was made

    def __str__(self):
        return f"Manager {self.manager.name} - {self.current_bonus_points} points available"

class BonusSettlement(models.Model):
    manager = models.ForeignKey(
        ManagerPersonalDetails, on_delete=models.CASCADE, related_name='bonus_settlements'
    )
    bonusRecords = models.ForeignKey(
        BonusRecords, related_name='settlements', on_delete=models.CASCADE,
    )
    bonus_points_used = models.PositiveIntegerField()
    remaining_bonus_points = models.PositiveIntegerField()
    settlement_title = models.CharField(max_length=300)
    settlement_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Settlement - {self.bonus_points_used} points"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure bonus points are updated and
        there are sufficient bonus points before creating a settlement.
        """
        # Get the current bonus points for the manager
        try:
            bonus_record = BonusRecords.objects.get(manager=self.manager)
        except BonusRecords.DoesNotExist:
            raise ValueError("Bonus record for the manager does not exist.")
        
        current_points = bonus_record.current_bonus_points

        # Ensure that enough bonus points are available for settlement
        if self.bonus_points_used > current_points:
            raise ValueError("Insufficient bonus points for this settlement.")

        # Calculate remaining bonus points after settlement
        self.remaining_bonus_points = current_points - self.bonus_points_used

        # Update the BonusRecords (manager's available bonus points)
        bonus_record.current_bonus_points = self.remaining_bonus_points
        bonus_record.save()

        # Save the settlement record
        super().save(*args, **kwargs)

    def add_transactions(self, transaction_list):
        """
        Method to add transactions to the settlement.
        """
        for transaction in transaction_list:
            self.transactions.add(transaction)
        self.save()

