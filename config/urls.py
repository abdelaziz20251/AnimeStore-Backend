"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.utils import timezone
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def api_root(request):
    """Root endpoint that provides API information."""
    return JsonResponse({
        'message': 'E-Commerce API',
        'version': '1.0.0',
        'status': 'operational',
        'endpoints': {
            'admin': '/admin/',
            'api_docs_swagger': '/api/schema/swagger-ui/',
            'api_docs_redoc': '/api/schema/redoc/',
            'users': {
                'register': '/api/users/register/',
                'login': '/api/users/login/',
                'logout': '/api/users/logout/',
                'me': '/api/users/me/',
            },
            'products': {
                'list': '/api/products/',
                'detail': '/api/products/{slug}/',
            },
            'categories': {
                'list': '/api/categories/',
                'detail': '/api/categories/{id}/',
            },
            'orders': {
                'list': '/api/orders/',
                'detail': '/api/orders/{id}/',
            },
            'sellers': {
                'profile': '/api/sellers/profile/',
                'products': '/api/sellers/products/',
            },
            'analytics': {
                'dashboard': '/api/analytics/dashboard/',
            },
        },
        'frontend': 'http://localhost:3000',
        'documentation': 'Visit /api/schema/swagger-ui/ for interactive API documentation',
    })


def health_check(request):
    """Health check endpoint for Render.com monitoring."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': str(timezone.now()),
        'version': '1.0.0',
        'service': 'e-commerce-api'
    })

urlpatterns = [
    # Root - API Information
    path('', api_root, name='api-root'),
    
    # Health Check
    path('health/', health_check, name='health-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/', include('users.urls')),
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/sellers/', include('sellers.urls')),
    path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
