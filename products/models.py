from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid
import random
import string


class Category(models.Model):
    """Product categories for organization and filtering."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Core product model with seller relationship."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'role': 'seller'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    
    # Basic Information
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Discount percentage (0-100)"
    )
    shipping_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        help_text="Shipping fee for this product"
    )
    
    # Inventory
    stock = models.PositiveIntegerField(default=0)
    
    # Product metadata
    sku = models.CharField(max_length=100, unique=True, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    tags = models.JSONField(default=list, blank=True, help_text="Product tags as list")
    
    # Technical Specifications (flexible JSON field)
    technical_specs = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Technical specifications as key-value pairs"
    )
    
    # Policies
    refund_policy = models.TextField(
        blank=True,
        default="30-day money-back guarantee",
        help_text="Refund/return policy for this product"
    )
    
    # Images
    image_url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    deletion_requested = models.BooleanField(default=False, help_text="Request for product deletion pending admin approval")
    deletion_requested_at = models.DateTimeField(null=True, blank=True, help_text="When the deletion was requested")
    
    # Reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = self.generate_unique_slug()
        
        # Auto-generate SKU only on creation (when pk is None)
        if not self.pk and not self.sku:
            self.sku = self.generate_sku()
        
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        """Generate a unique slug from product name."""
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        
        while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    @staticmethod
    def generate_sku():
        """Generate a unique SKU (Stock Keeping Unit)."""
        # Format: PRD-YYYYMMDD-XXXXX (e.g., PRD-20251024-A3F9K)
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        sku = f"PRD-{date_str}-{random_str}"
        
        # Ensure uniqueness
        while Product.objects.filter(sku=sku).exists():
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            sku = f"PRD-{date_str}-{random_str}"
        
        return sku
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    @property
    def discounted_price(self):
        """Calculate price after discount."""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
    @property
    def final_price(self):
        """Calculate final price including shipping."""
        return self.discounted_price + self.shipping_fee


class ProductImage(models.Model):
    """Additional product images (gallery)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    """Customer reviews and ratings."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}★)"
