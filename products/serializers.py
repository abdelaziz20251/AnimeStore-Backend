from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for ProductReview model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'user_email', 'user_name', 'rating', 
                  'title', 'comment', 'is_verified_purchase', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_verified_purchase', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'stock', 'in_stock', 'image_url', 
                  'thumbnail_url', 'category_name', 'seller_name', 'is_featured', 
                  'is_active', 'deletion_requested', 'deletion_requested_at', 
                  'average_rating', 'review_count', 'created_at']
        read_only_fields = ['id', 'in_stock', 'deletion_requested', 'deletion_requested_at', 
                          'average_rating', 'review_count', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view."""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'seller', 'seller_name', 'category', 'category_id', 'name', 
                  'slug', 'description', 'price', 'discount_percentage', 'discounted_price',
                  'shipping_fee', 'final_price', 'stock', 'in_stock', 'sku', 'brand', 
                  'weight', 'tags', 'technical_specs', 'refund_policy',
                  'image_url', 'thumbnail_url', 'images', 'is_active', 
                  'is_featured', 'deletion_requested', 'deletion_requested_at',
                  'reviews', 'average_rating', 'review_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'seller', 'in_stock', 'discounted_price', 'final_price', 
                            'deletion_requested', 'deletion_requested_at', 'average_rating', 
                            'review_count', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products."""
    
    # Optional fields for flexibility
    slug = serializers.SlugField(required=False, allow_blank=True)
    sku = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.JSONField(required=False)
    technical_specs = serializers.JSONField(required=False)
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'discount_percentage',
                  'shipping_fee', 'stock', 'sku', 'brand', 'weight', 'tags', 'technical_specs',
                  'refund_policy', 'image_url', 'thumbnail_url', 'is_active', 'is_featured',
                  'deletion_requested', 'deletion_requested_at']
        read_only_fields = ['deletion_requested', 'deletion_requested_at']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_discount_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value
    
    def validate_shipping_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Shipping fee cannot be negative.")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value
    
    def validate_tags(self, value):
        """Ensure tags is a list of strings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        if not all(isinstance(tag, str) for tag in value):
            raise serializers.ValidationError("All tags must be strings.")
        return value
    
    def validate_technical_specs(self, value):
        """Ensure technical_specs is a dictionary."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Technical specifications must be a dictionary.")
        return value

