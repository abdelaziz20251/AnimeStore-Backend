from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerProfileViewSet, SellerPayoutViewSet, SellerOrderViewSet

router = DefaultRouter()
router.register(r'profiles', SellerProfileViewSet, basename='seller-profile')
router.register(r'payouts', SellerPayoutViewSet, basename='seller-payout')
router.register(r'orders', SellerOrderViewSet, basename='seller-order')

urlpatterns = [
    path('', include(router.urls)),
]

