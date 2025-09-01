"""
URL patterns for the voting system API
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import generics, permissions
from . import views
from .serializers import UserProfileSerializer

app_name = 'core'

urlpatterns = [
    # JWT Authentication (nativo de SimpleJWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User Profile (usando DRF generic views)
    path('api/profile/', generics.RetrieveUpdateAPIView.as_view(
        serializer_class=UserProfileSerializer,
        permission_classes=[permissions.IsAuthenticated]
    ), name='profile'),
    
    # GitHub OAuth personalizado con manejo de state
    path('social/github/login/', views.custom_github_login, name='custom_github_login'),
    
    # Obtener tokens JWT
    path('api/tokens/', views.create_tokens, name='create_tokens'),
] 