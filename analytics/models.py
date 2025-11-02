from django.db import models
from django.conf import settings
from products.models import Product


class ProductView(models.Model):
    """Track product page views for analytics."""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='views'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Session tracking
    session_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Referrer
    referrer = models.URLField(max_length=500, blank=True)
    
    # Timestamp
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_views'
        indexes = [
            models.Index(fields=['product', '-viewed_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"View of {self.product.name} at {self.viewed_at}"


class SearchQuery(models.Model):
    """Track search queries for analytics and recommendations."""
    
    query = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Results
    results_count = models.PositiveIntegerField(default=0)
    
    # Session tracking
    session_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamp
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        indexes = [
            models.Index(fields=['-searched_at']),
            models.Index(fields=['query']),
        ]
        verbose_name_plural = 'Search queries'
    
    def __str__(self):
        return f"Search: {self.query}"


class CartActivityLog(models.Model):
    """Log cart activities for analytics (triggered by Supabase Edge)."""
    
    ACTION_CHOICES = (
        ('add', 'Add Item'),
        ('remove', 'Remove Item'),
        ('update', 'Update Quantity'),
        ('clear', 'Clear Cart'),
        ('checkout', 'Checkout'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    
    # Session tracking
    session_id = models.CharField(max_length=100)
    
    # Snapshot
    cart_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_activity_logs'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.product.name if self.product else 'N/A'}"


class SalesMetrics(models.Model):
    """Aggregated daily sales metrics."""
    
    date = models.DateField(unique=True)
    
    # Orders
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    
    # Revenue
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Products
    total_products_sold = models.PositiveIntegerField(default=0)
    unique_products_sold = models.PositiveIntegerField(default=0)
    
    # Users
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_metrics'
        ordering = ['-date']
        verbose_name_plural = 'Sales metrics'
    
    def __str__(self):
        return f"Metrics for {self.date}"
