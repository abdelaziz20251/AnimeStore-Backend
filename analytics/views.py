from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import ProductView, SearchQuery, CartActivityLog, SalesMetrics
from .serializers import (
    ProductViewSerializer,
    SearchQuerySerializer,
    CartActivityLogSerializer,
    SalesMetricsSerializer
)


class ProductViewViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductView operations."""
    
    queryset = ProductView.objects.select_related('product', 'user')
    serializer_class = ProductViewSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending products based on views."""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        trending = ProductView.objects.filter(
            viewed_at__gte=since
        ).values('product__id', 'product__name').annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:10]
        
        return Response(trending)


class SearchQueryViewSet(viewsets.ModelViewSet):
    """ViewSet for SearchQuery operations."""
    
    queryset = SearchQuery.objects.select_related('user')
    serializer_class = SearchQuerySerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular search queries."""
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        
        popular = SearchQuery.objects.filter(
            searched_at__gte=since
        ).values('query').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:20]
        
        return Response(popular)


class CartActivityLogViewSet(viewsets.ModelViewSet):
    """ViewSet for CartActivityLog operations."""
    
    queryset = CartActivityLog.objects.select_related('user', 'product')
    serializer_class = CartActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]


class SalesMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SalesMetrics operations."""
    
    queryset = SalesMetrics.objects.all()
    serializer_class = SalesMetricsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get sales summary for a date range."""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = SalesMetrics.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_orders=Sum('total_orders'),
            completed_orders=Sum('completed_orders'),
            cancelled_orders=Sum('cancelled_orders'),
            total_revenue=Sum('total_revenue'),
            total_products_sold=Sum('total_products_sold'),
            new_users=Sum('new_users'),
            active_users=Sum('active_users')
        )
        
        return Response(metrics)
