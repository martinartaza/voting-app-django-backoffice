"""
Custom managers for company-based filtering

These managers provide methods to filter querysets based on the user's company.
"""

from django.db import models
from django.contrib.auth.models import BaseUserManager


class CompanyFilterManager(BaseUserManager):
    """
    Manager base que proporciona filtrado por compañía
    """
    
    def for_company(self, company):
        """Filtra objetos por compañía específica"""
        return self.filter(company=company)
    
    def for_user(self, user):
        """
        Filtra objetos basado en la compañía del usuario.
        Los administradores pueden ver todo.
        """
        if user.is_superuser or user.role == 'ADMIN':
            return self.all()
        return self.filter(company=user.company)


class CompetitionManager(models.Manager):
    """
    Manager personalizado para Competition con filtrado por compañía
    """
    
    def for_company(self, company):
        """Filtra objetos por compañía específica"""
        return self.filter(creator__company=company)
    
    def for_user(self, user):
        """
        Filtra competencias basado en la compañía del usuario.
        Los administradores pueden ver todo.
        """
        if user.is_superuser or user.role == 'ADMIN':
            return self.all()
        return self.filter(creator__company=user.company)


class VoteManager(models.Manager):
    """
    Manager personalizado para Vote con filtrado por compañía
    """
    
    def for_company(self, company):
        """Filtra objetos por compañía específica"""
        return self.filter(competition__creator__company=company)
    
    def for_user(self, user):
        """
        Filtra votos basado en la compañía del usuario.
        Los administradores pueden ver todo.
        """
        if user.is_superuser or user.role == 'ADMIN':
            return self.all()
        return self.filter(competition__creator__company=user.company)


class UserManager(CompanyFilterManager):
    """
    Manager personalizado para CustomUser con filtrado por compañía
    """
    
    def for_user(self, user):
        """
        Filtra usuarios basado en la compañía del usuario.
        Los administradores pueden ver todo.
        """
        if user.is_superuser or user.role == 'ADMIN':
            return self.all()
        return self.filter(company=user.company)
    
    def get_by_natural_key(self, username):
        """
        Método requerido por Django para autenticación.
        Permite autenticación por username.
        """
        return self.get(username=username)
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular.
        """
        if not username:
            raise ValueError('El username es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Crea y guarda un superusuario.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields) 