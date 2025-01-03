from django.contrib import admin

from vso_app.models import BonusRecords, BonusSettlement
from .models import ManagerPersonalDetails

class ManagerPersonalDetailsAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view
    list_display = ('manager_id', 'name', 'contact_no', 'email', 'district', 'taluka', 'dob', 'gender')
    
    # Add search functionality for these fields
    search_fields = ('name', 'contact_no', 'email', 'district', 'taluka')
    
    # Add filtering options for these fields
    list_filter = ('district', 'taluka', 'gender')

# Register the model with the customized admin
admin.site.register(ManagerPersonalDetails, ManagerPersonalDetailsAdmin)

@admin.register(BonusRecords)
class BonusRecordsAdmin(admin.ModelAdmin):
    list_display = ('manager', 'current_bonus_points', 'last_updated_at')
    search_fields = ('manager__name',)
    ordering = ('-last_updated_at',)
    list_per_page = 25

@admin.register(BonusSettlement)
class BonusSettlementAdmin(admin.ModelAdmin):
    list_display = ('manager', 'bonus_points_used', 'created_at')
    search_fields = ('manager__name',)
    ordering = ('-created_at',)
    list_per_page = 25