from django.contrib import admin
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal', 'added_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at', 'updated_at']
    search_fields = ['user__email']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'product_name', 'product_sku', 'price', 'quantity', 'subtotal']
    readonly_fields = ['subtotal']
    autocomplete_fields = ['product']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    autocomplete_fields = ['user']
    
    def save_formset(self, request, form, formset, change):
        """Auto-populate order item fields from product and recalculate totals."""
        instances = formset.save(commit=False)
        
        # Save each instance with auto-population
        for instance in instances:
            if isinstance(instance, OrderItem) and instance.product:
                # Auto-populate from product if fields are empty
                if not instance.product_name:
                    instance.product_name = instance.product.name
                if not instance.product_sku:
                    instance.product_sku = instance.product.sku
                if not instance.price:
                    instance.price = instance.product.price
                instance.save()
        
        # Delete objects marked for deletion
        for obj in formset.deleted_objects:
            obj.delete()
        
        # Save many-to-many relationships
        formset.save_m2m()
        
        # Recalculate order totals
        order = form.instance
        items = order.items.all()
        
        if items.exists():
            subtotal = sum(
                Decimal(str(item.price)) * item.quantity 
                for item in items 
                if item.price and item.quantity
            )
            order.subtotal = Decimal(str(subtotal))
            order.tax = order.subtotal * Decimal('0.10')
            order.shipping_cost = order.shipping_cost or Decimal('0.00')
            order.total = order.subtotal + order.tax + order.shipping_cost
            order.save()
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total'),
            'description': 'These will be auto-calculated from order items'
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_zip', 'shipping_country', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']
