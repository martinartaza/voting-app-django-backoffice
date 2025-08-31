from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from core.models import Company
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.SUCCESS('Superuser already exists. Skipping creation.')
            )
            return

        # Get credentials from environment variables
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        company_name = os.getenv('DJANGO_SUPERUSER_COMPANY', 'Default Company')

        try:
            # Create or get default company
            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={'name': company_name}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created default company: {company_name}')
                )

            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                company=company,
                role='ADMIN'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {username} in company: {company_name}'
                )
            )
            
            # Print credentials for first deployment
            self.stdout.write(
                self.style.WARNING(
                    f'\n=== SUPERUSER CREDENTIALS ===\n'
                    f'Username: {username}\n'
                    f'Password: {password}\n'
                    f'Email: {email}\n'
                    f'Company: {company_name}\n'
                    f'Role: ADMIN\n'
                    f'================================\n'
                )
            )
            
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING('Superuser creation failed. User might already exist.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            ) 