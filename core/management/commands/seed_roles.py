# core/management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from core.models import Role, Permission

class Command(BaseCommand):
    help = "Seeds initial roles"

    def handle(self, *args, **options):
        # We assume permissions are seeded
        admin_role, _ = Role.objects.get_or_create(name='PLATFORM_ADMIN', defaults={'is_system_role': True})
        participant_role, _ = Role.objects.get_or_create(name='PARTICIPANT', defaults={'is_system_role': True})
        
        # Add all perms to admin
        for p in Permission.objects.all():
            admin_role.permissions.add(p)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded roles.'))
