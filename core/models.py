from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CompetitionManager, VoteManager, UserManager

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    COMPANY_ADMIN = 'COMPANY_ADMIN', 'Administrador de Empresa'
    COMMON_USER = 'COMMON_USER', 'Usuario Común'

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nombre de la Empresa")
    # Puedes añadir más campos aquí si lo necesitas, como dirección, etc.

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.COMMON_USER,
        verbose_name="Rol de Usuario"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Empresa"
    )

    objects = UserManager()

    class Meta:
        verbose_name = "Usuario Personalizado"
        verbose_name_plural = "Usuarios Personalizados"

    def __str__(self):
        return self.username

    def can_access_company(self, company):
        """Verifica si el usuario puede acceder a una compañía específica"""
        if self.is_superuser or self.role == 'ADMIN':
            return True
        return self.company == company


class Competition(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Competition Name",
        help_text="Name of the competition (e.g., 'Best Colleague 2024')"
    )
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competitions_created',
        verbose_name="Creador"
    )


    objects = CompetitionManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Competition"
        verbose_name_plural = "Competitions"


class Vote(models.Model):
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        verbose_name="Related Competition"
    )
    title = models.CharField(
        max_length=100,
        verbose_name="Vote Title",
        help_text="Title of the vote (e.g., 'Most Helpful Colleague')"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Optional details about the vote"
    )
    award = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Award",
        help_text="Prize or recognition for the winner"
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name="Is Public?",
        help_text="Check if the vote is visible to all employees"
    )

    voter = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='votes_made',
        verbose_name="Votante",
        null=True
    )

    nominee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='votes_received',
        verbose_name="Nominado",
        null=True
    )

    objects = VoteManager()

    def __str__(self):
        return f"{self.title} ({self.competition.name})"

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

    @property
    def company(self):
        """Obtiene la compañía a través de la competencia y su creador"""
        return self.competition.creator.company


class EmailVerification(models.Model):
    """Modelo para verificación de email"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Verification for {self.user.email}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
