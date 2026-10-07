# core/management/commands/seed_permissions.py
from django.core.management.base import BaseCommand
from core.models import Permission

class Command(BaseCommand):
    help = "Seeds initial permissions"

    def handle(self, *args, **options):
        perms = [
            {'slug': 'view_dashboard', 'name': 'View Dashboard', 'description': ''},
            {'slug': 'manage_users', 'name': 'Manage Users', 'description': ''},
            {'slug': 'manage_organizations', 'name': 'Manage Organizations', 'description': ''},
        ]
        for p in perms:
            Permission.objects.update_or_create(slug=p['slug'], defaults={'name': p['name'], 'description': p['description']})
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded permissions.'))
