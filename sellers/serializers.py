from rest_framework import serializers
from .models import SellerProfile, SellerPayout


class SellerProfileSerializer(serializers.ModelSerializer):
    """Serializer for Seller Profile."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SellerProfile
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'business_name', 'business_description', 'business_email',
            'business_phone', 'business_address', 'business_city',
            'business_state', 'business_zip', 'business_country',
            'tax_id', 'business_license', 
            'bank_account_holder', 'bank_account_number', 'bank_routing_number', 'bank_name', 'bank_address',
            'is_verified', 'is_active',
            'average_rating', 'total_reviews', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'is_verified', 'average_rating', 'total_reviews', 'verified_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class SellerPayoutSerializer(serializers.ModelSerializer):
    """Serializer for Seller Payout."""
    
    seller_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SellerPayout
        fields = [
            'id', 'seller', 'seller_name', 'amount', 'status',
            'period_start', 'period_end', 'transaction_id', 'notes',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['seller', 'created_at', 'processed_at']
    
    def get_seller_name(self, obj):
        try:
            profile = SellerProfile.objects.get(user=obj.seller)
            return profile.business_name
        except SellerProfile.DoesNotExist:
            return obj.seller.username
