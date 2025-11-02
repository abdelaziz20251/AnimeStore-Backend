from django.db import models
from django.conf import settings


class SellerProfile(models.Model):
    """Extended profile information for sellers."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile',
        limit_choices_to={'role': 'seller'}
    )
    
    # Business information
    business_name = models.CharField(max_length=255)
    business_description = models.TextField(blank=True)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=20)
    
    # Address
    business_address = models.TextField()
    business_city = models.CharField(max_length=100)
    business_state = models.CharField(max_length=100)
    business_zip = models.CharField(max_length=20)
    business_country = models.CharField(max_length=100)
    
    # Tax & Legal
    tax_id = models.CharField(max_length=50, blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    
    # Banking (for payouts)
    bank_account_holder = models.CharField(max_length=255, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_routing_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bank_address = models.TextField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'seller_profiles'
    
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"


class SellerPayout(models.Model):
    """Track payouts to sellers."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts',
        limit_choices_to={'role': 'seller'}
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Period covered
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'seller_payouts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout to {self.seller.email} - ${self.amount}"
