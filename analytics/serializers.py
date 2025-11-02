from rest_framework import serializers
from .models import ProductView, SearchQuery, CartActivityLog, SalesMetrics


class ProductViewSerializer(serializers.ModelSerializer):
    """Serializer for ProductView model."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = ProductView
        fields = ['id', 'product', 'product_name', 'user', 'user_email', 
                  'session_id', 'ip_address', 'user_agent', 'referrer', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for SearchQuery model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = SearchQuery
        fields = ['id', 'query', 'user', 'user_email', 'results_count', 
                  'session_id', 'ip_address', 'searched_at']
        read_only_fields = ['id', 'searched_at']


class CartActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for CartActivityLog model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CartActivityLog
        fields = ['id', 'user', 'user_email', 'product', 'product_name', 'action', 
                  'quantity', 'session_id', 'cart_total', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalesMetricsSerializer(serializers.ModelSerializer):
    """Serializer for SalesMetrics model."""
    
    class Meta:
        model = SalesMetrics
        fields = ['id', 'date', 'total_orders', 'completed_orders', 'cancelled_orders', 
                  'total_revenue', 'total_tax', 'total_shipping', 'total_products_sold', 
                  'unique_products_sold', 'new_users', 'active_users', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

