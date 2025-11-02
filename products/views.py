from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Avg
from django.core.files.storage import default_storage
from .models import Category, Product, ProductImage, ProductReview
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ProductReviewSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category operations."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product operations."""
    
    queryset = Product.objects.select_related('category', 'seller').prefetch_related('images', 'reviews')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku', 'brand']
    ordering_fields = ['price', 'created_at', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by seller
        seller = self.request.query_params.get('seller', None)
        if seller:
            queryset = queryset.filter(seller__id=seller)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(price__gte=min_price)
            except (ValueError, TypeError):
                pass  # Skip invalid min_price
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(price__lte=max_price)
            except (ValueError, TypeError):
                pass  # Skip invalid max_price
        
        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        # Filter by featured
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Only show active products to users, EXCEPT:
        # 1. When a seller is viewing their own products (for product management page)
        # 2. When performing update/delete operations (to allow modifying inactive products)
        seller_id = self.request.query_params.get('seller', None)
        viewing_own_products = (seller_id and self.request.user.is_authenticated and 
                                 str(seller_id) == str(self.request.user.id))
        is_update_action = self.action in ['update', 'partial_update', 'destroy']
        
        if not (viewing_own_products or is_update_action):
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def perform_update(self, serializer):
        # Only allow seller to update their own products
        if serializer.instance.seller != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only update your own products.')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete: Mark product for deletion instead of actually deleting."""
        from django.utils import timezone
        
        # Only the seller or admin can request deletion
        if instance.seller != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete your own products or be an admin.')
        
        # If admin is deleting, actually delete the product
        if self.request.user.is_staff:
            instance.delete()
        else:
            # If seller is deleting, mark for admin approval
            instance.deletion_requested = True
            instance.deletion_requested_at = timezone.now()
            instance.is_active = False  # Hide product immediately
            instance.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, slug=None):
        """Add a review to a product."""
        product = self.get_object()
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get all reviews for a product."""
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request):
        """Upload product image to local storage"""
        try:
            if 'image' not in request.FILES:
                return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validate file type
            valid_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if image_file.content_type not in valid_types:
                return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file size (5MB max)
            if image_file.size > 5 * 1024 * 1024:
                return Response({'error': 'File too large (max 5MB)'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save file to media storage
            filename = f"products/{image_file.name}"
            path = default_storage.save(filename, image_file)
            url = request.build_absolute_uri(default_storage.url(path))
            
            return Response({
                'url': url,
                'path': path,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductReview operations."""
    
    queryset = ProductReview.objects.select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product__id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        self.update_product_ratings(review.product)
    
    def perform_update(self, serializer):
        review = serializer.save()
        self.update_product_ratings(review.product)
    
    def perform_destroy(self, instance):
        product = instance.product
        instance.delete()
        self.update_product_ratings(product)
    
    def update_product_ratings(self, product):
        """Update product's average rating and review count."""
        reviews = ProductReview.objects.filter(product=product)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        review_count = reviews.count()
        
        Product.objects.filter(id=product.id).update(
            average_rating=round(avg_rating, 2),
            review_count=review_count
        )
