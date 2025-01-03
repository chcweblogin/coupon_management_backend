from django.contrib import admin
from .models import (
    CreditRepayment, CreditRepaymentDetail, DoctorCredit, DoctorPersonalDetails, 
    Gifts, StockTransaction, TransactionDetail, VSOPersonalDetails, Product, 
    Coupon, Transaction, Settlement, VSOProductStock
)

@admin.register(VSOPersonalDetails)
class VSOPersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ('vso_id', 'name', 'contact_no', 'email', 'district', 'taluka', 'manager')
    search_fields = ('name', 'contact_no', 'email', 'district', 'taluka')  # Searchable fields
    list_filter = ('district', 'taluka', 'manager')  # Filters


@admin.register(DoctorPersonalDetails)
class DoctorPersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'name', 'district', 'taluka', 'village', 'mobile_no', 'email')
    search_fields = ('name', 'mobile_no', 'email', 'district', 'taluka', 'village')
    list_filter = ('district', 'taluka', 'village')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'product_type', 'market_price', 'settlement_points', 'coupon_value')
    search_fields = ('name', 'product_type')
    list_filter = ('product_type',)





@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'vso', 'doctor', 'total_points_used', 'status', 'date_transaction', 'time_transaction')
    search_fields = ('vso__name', 'doctor__name')  # Assuming VSO and Doctor have name fields
    list_filter = ('status', 'date_transaction')


@admin.register(TransactionDetail)
class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = ('detail_id', 'transaction', 'product', 'previous_points', 'points_used', 'quantity_redeemed')
    search_fields = ('transaction__transaction_id', 'product__name')  # Assuming Product has a name field
    list_filter = ('product',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_id', 'vso', 'doctor', 'product', 'coupon_points', 'current_points', 'status', 'date_collected')
    search_fields = ('vso__name', 'doctor__name', 'product__name')  # Assuming VSO, Doctor, and Product have name fields
    list_filter = ('status', 'date_collected')


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('settlement_id', 'vso', 'doctor', 'product', 'points_settled_value', 'credit_borrowed_points', 'remaining_points_value', 'quantity', 'product_type', 'date_settled')
    search_fields = ('vso__name', 'doctor__name', 'product__name')
    list_filter = ('product_type', 'date_settled')


@admin.register(DoctorCredit)
class DoctorCreditAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'product', 'borrowed_points', 'repaid_points', 'repay_status', 'date_issued', 'date_repaid')
    search_fields = ('doctor__name', 'product__name')
    list_filter = ('repay_status', 'date_issued', 'date_repaid')


@admin.register(CreditRepayment)
class CreditRepaymentAdmin(admin.ModelAdmin):
    list_display = ('credit', 'transaction', 'date_repaid')
    search_fields = ('credit__doctor__name', 'transaction__transaction_id')  # Assuming Doctor has a name field
    list_filter = ('date_repaid',)


@admin.register(CreditRepaymentDetail)
class CreditRepaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('repayment', 'product', 'coupon', 'points_repaid')
    search_fields = ('repayment__credit__doctor__name', 'product__name', 'coupon__coupon_id')
    list_filter = ('product',)


@admin.register(VSOProductStock)
class VSOProductStockAdmin(admin.ModelAdmin):
    list_display = ('vso', 'product', 'current_stock')
    search_fields = ('vso__name', 'product__name')
    list_filter = ('vso', 'product')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('vso_product_stock', 'transaction_type', 'used_quantity', 'transaction_date')
    search_fields = ('vso_product_stock__vso__name', 'vso_product_stock__product__name')
    list_filter = ('transaction_type', 'transaction_date')


@admin.register(Gifts)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('gift_name', 'gift_price', 'settlement')
    search_fields = ('gift_name',)
    list_filter = ('settlement',)
