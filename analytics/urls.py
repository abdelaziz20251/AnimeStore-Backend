from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewViewSet,
    SearchQueryViewSet,
    CartActivityLogViewSet,
    SalesMetricsViewSet
)

router = DefaultRouter()
router.register(r'product-views', ProductViewViewSet, basename='product-view')
router.register(r'search-queries', SearchQueryViewSet, basename='search-query')
router.register(r'cart-activity', CartActivityLogViewSet, basename='cart-activity')
router.register(r'sales-metrics', SalesMetricsViewSet, basename='sales-metrics')

urlpatterns = [
    path('', include(router.urls)),
]

