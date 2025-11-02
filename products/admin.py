from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image_url', 'alt_text', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock', 'seller', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'sku', 'brand', 'description', 'seller__username']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    autocomplete_fields = ['seller', 'category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'seller')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_percentage', 'shipping_fee')
        }),
        ('Inventory', {
            'fields': ('stock', 'sku', 'brand', 'weight')
        }),
        ('Additional Information', {
            'fields': ('tags', 'technical_specs', 'refund_policy'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('image_url', 'thumbnail_url')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['product', 'user']
