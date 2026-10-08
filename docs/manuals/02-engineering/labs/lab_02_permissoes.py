from _lab_base import run_lab, load_mock_personas
from core.models import OrganizationMembership, Role, Permission, UserProfile
from django.contrib.auth.models import User
from core.middleware import _check_permission

def lab_permissoes():
    org_uf, org_emp = load_mock_personas()
    
    prof, _ = User.objects.get_or_create(username="prof.ana.lab2", defaults={"email": "prof.ana2@example.org"})
    UserProfile.objects.get_or_create(user=prof)
    sysadmin, _ = User.objects.get_or_create(username="admin.lab2", defaults={"email": "admin2@example.org"})
    sysadmin_profile, _ = UserProfile.objects.get_or_create(user=sysadmin)
    sysadmin_role, _ = Role.objects.get_or_create(slug="platform_admin", defaults={"name": "Platform Admin", "scope": Role.Scope.PLATFORM})
    perm, _ = Permission.objects.get_or_create(slug="org.manage_whatsapp", defaults={"name": "Manage WhatsApp"})
    sysadmin_role.permissions.add(perm)
    sysadmin_profile.platform_role = sysadmin_role
    sysadmin_profile.save()

    # Org Role (prof)
    org_manager_role, _ = Role.objects.get_or_create(slug="org_manager", defaults={"name": "Org Manager", "scope": Role.Scope.ORGANIZATION})
    org_manager_role.permissions.add(perm)
    
    OrganizationMembership.objects.create(
        organization=org_uf,
        user=prof,
        role=org_manager_role
    )

    print("--- Cenário 1: Usuário sem permissão ---")
    anon, _ = User.objects.get_or_create(username="anon.lab2", defaults={"email": "anon2@example.org"})
    UserProfile.objects.get_or_create(user=anon)
    print(f"Anon tem org.manage_whatsapp? {_check_permission(anon, 'org.manage_whatsapp')}")

    print("\n--- Cenário 2: Platform Role ---")
    print(f"Sysadmin tem org.manage_whatsapp? {_check_permission(sysadmin, 'org.manage_whatsapp')}")

    print("\n--- Cenário 3: Org Membership ---")
    print(f"Prof. Ana tem org.manage_whatsapp? {_check_permission(prof, 'org.manage_whatsapp')}")

if __name__ == '__main__':
    run_lab(lab_permissoes)
