"""
Serializers for the voting system API
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Company, EmailVerification
from datetime import timedelta
from django.utils import timezone
import uuid


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para Company"""
    
    class Meta:
        model = Company
        fields = ['id', 'name']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    company_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'company_name', 'company_email'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return attrs
    
    def create(self, validated_data):
        # Extraer datos de la compañía
        company_name = validated_data.pop('company_name')
        company_email = validated_data.pop('company_email')
        password_confirm = validated_data.pop('password_confirm')
        
        # Crear o obtener la compañía
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={'name': company_name}
        )
        
        # Crear el usuario
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            company=company,
            role='COMMON_USER',
            is_active=False  # Usuario inactivo hasta verificar email
        )
        
        # Crear verificación de email
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=24)
        
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuario"""
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'company', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined'] 