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
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


@csrf_exempt
def api_root(request):
    """Root endpoint that provides API information - CSRF exempt for health checks."""
    try:
        return JsonResponse({
            'message': 'E-Commerce API',
            'version': '1.0.0',
            'status': 'operational',
            'health': '/health/',
            'docs': '/api/schema/swagger-ui/',
        })
    except Exception:
        # Fallback if anything fails
        return JsonResponse({'status': 'ok'}, status=200)


@csrf_exempt
def health_check(request):
    """Health check endpoint for Railway monitoring - minimal, no dependencies."""
    # Ultra-simple health check - no database, no timezone, no dependencies
    return JsonResponse({'status': 'healthy'}, status=200)

urlpatterns = [
    # Health Check (must be first for Railway healthcheck)
    path('health/', health_check, name='health-check'),
    path('health', health_check, name='health-check-no-slash'),
    
    # Root - API Information
    path('', api_root, name='api-root'),
    
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
