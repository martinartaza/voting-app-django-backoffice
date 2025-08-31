from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import render
from .serializers import UserRegistrationSerializer
from .models import EmailVerification
from django.utils import timezone
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
import uuid


User = get_user_model()


def index_view(request):
    return render(request, 'index.html')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Registra un nuevo usuario con verificación de email
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Obtener el token de verificación
        verification = EmailVerification.objects.get(user=user)
        
        # Enviar email de verificación usando django-allauth
        
        # Crear EmailAddress si no existe
        email_address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={'primary': True}
        )
        
        # Enviar email de confirmación usando el método de EmailAddress
        email_address.send_confirmation(request, signup=True)
        
        return Response({
            'message': 'Usuario registrado exitosamente. Verifica tu email para activar la cuenta.',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

