from django.contrib import admin
from .models import SellerProfile, SellerPayout


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'is_verified', 'is_active', 'average_rating', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['business_name', 'user__email', 'business_email']
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_description', 'business_email', 'business_phone')
        }),
        ('Address', {
            'fields': ('business_address', 'business_city', 'business_state', 
                      'business_zip', 'business_country')
        }),
        ('Legal', {
            'fields': ('tax_id', 'business_license')
        }),
        ('Banking', {
            'fields': ('bank_account_holder', 'bank_account_number', 'bank_routing_number')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'verified_at')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SellerPayout)
class SellerPayoutAdmin(admin.ModelAdmin):
    list_display = ['seller', 'amount', 'status', 'period_start', 'period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['seller__email', 'transaction_id']
    readonly_fields = ['created_at', 'processed_at']
