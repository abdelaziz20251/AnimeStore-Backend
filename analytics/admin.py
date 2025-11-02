from django.contrib import admin
from .models import ProductView, SearchQuery, CartActivityLog, SalesMetrics


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'session_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['product__name', 'user__email', 'session_id']
    readonly_fields = ['viewed_at']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'searched_at']
    list_filter = ['searched_at']
    search_fields = ['query', 'user__email']
    readonly_fields = ['searched_at']


@admin.register(CartActivityLog)
class CartActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'action', 'quantity', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at']


@admin.register(SalesMetrics)
class SalesMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'completed_orders', 'total_revenue', 'new_users']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
