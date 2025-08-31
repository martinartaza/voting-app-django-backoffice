from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up the production site for django-allauth'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if site already exists with correct domain',
        )

    def handle(self, *args, **options):
        # Get the domain from settings or environment
        domain = getattr(settings, 'PRODUCTION_DOMAIN', None)
        
        if not domain:
            # Try to get from environment variable
            domain = os.getenv('PRODUCTION_DOMAIN', 'django.sebastianartaza.com')
        
        self.stdout.write(f'Setting up site with domain: {domain}')
        
        # Check if site already exists with correct domain
        try:
            existing_site = Site.objects.get(id=1)
            if existing_site.domain == domain and existing_site.name == 'Voting System Django' and not options['force']:
                self.stdout.write(
                    self.style.SUCCESS(f'Site already configured correctly: {existing_site.name} ({existing_site.domain})')
                )
                return
            else:
                # Update existing site
                existing_site.domain = domain
                existing_site.name = 'Voting System Django'
                existing_site.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated existing site: {existing_site.name} ({existing_site.domain})')
                )
        except Site.DoesNotExist:
            # Create new site
            site = Site.objects.create(
                id=1,
                domain=domain,
                name='Voting System Django'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created new site: {site.name} ({site.domain})')
            )
        
        # List all sites for verification
        sites = Site.objects.all()
        self.stdout.write('\nAll sites:')
        for s in sites:
            self.stdout.write(f'  - ID: {s.id}, Name: {s.name}, Domain: {s.domain}')
