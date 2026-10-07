# core/management/commands/seed_demo.py
from django.core.management.base import BaseCommand
from core.models import Organization, UserProfile, Role
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = "Seeds demo organization and superuser"

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug='ai-control-platform', 
            defaults={'name': 'AI-Control Platform', 'org_type': 'PLATFORM'}
        )
        
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            admin_role = Role.objects.filter(name='PLATFORM_ADMIN').first()
            
            profile = UserProfile.objects.create(
                user=user,
                primary_organization=org
            )
            if admin_role:
                profile.roles.add(admin_role)
                
            self.stdout.write(self.style.SUCCESS('Successfully created admin user.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
