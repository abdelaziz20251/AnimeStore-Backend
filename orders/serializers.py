from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from products.models import Product
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 
                  'added_at', 'updated_at']
        read_only_fields = ['id', 'added_at', 'updated_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'price', 
                  'quantity', 'subtotal', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for OrderStatusHistory model."""
    
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'changed_by', 'changed_by_email', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order listings."""
    
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'total', 'items_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single order view."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'order_number', 'status', 'subtotal', 
                  'tax', 'shipping_cost', 'total', 'shipping_address', 'shipping_city', 
                  'shipping_state', 'shipping_zip', 'shipping_country', 'phone', 
                  'payment_method', 'payment_status', 'items', 'status_history', 
                  'created_at', 'updated_at', 'shipped_at', 'delivered_at']
        read_only_fields = ['id', 'user', 'order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_state', 
                  'shipping_zip', 'shipping_country', 'phone', 'payment_method']
    
    def validate(self, attrs):
        # Validate that user has items in cart
        user = self.context['request'].user
        if not hasattr(user, 'cart') or not user.cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Get or create cart
        try:
            cart = user.cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart is empty.")
        
        # Check cart has items
        if not cart.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        
        # Calculate totals (use Decimal for all calculations)
        subtotal = Decimal(str(cart.total_price))
        tax = subtotal * Decimal('0.10')  # 10% tax
        shipping_cost = Decimal('0.00')  # FREE shipping
        total = subtotal + tax + shipping_cost
        
        # Handle wallet payment
        payment_method = validated_data.get('payment_method', 'cash_on_delivery')
        payment_status = 'pending'
        
        if payment_method == 'wallet':
            # Check wallet balance
            if user.wallet_balance < total:
                raise serializers.ValidationError('Insufficient wallet balance.')
            
            # Deduct from wallet
            user.wallet_balance -= total
            user.save()
            payment_status = 'completed'
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            payment_status=payment_status,
            **validated_data
        )
        
        # Create order items from cart (save seller info for refund tracking)
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                price=cart_item.product.price,
                quantity=cart_item.quantity,
                seller=cart_item.product.seller  # Save seller for refund tracking
            )
            
            # Reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created',
            changed_by=user
        )
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)

