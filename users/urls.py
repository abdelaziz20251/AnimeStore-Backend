from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .views import UserViewSet
from .serializers import CustomTokenObtainSerializer, UserSerializer

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_token_obtain_pair(request):
    """Custom login view that accepts email instead of username."""
    serializer = CustomTokenObtainSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', custom_token_obtain_pair, name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

