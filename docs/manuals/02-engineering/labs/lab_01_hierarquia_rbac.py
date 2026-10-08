from _lab_base import run_lab, load_mock_personas
from core.models import Department, Project, Squad, OrganizationMembership, Role, JobTitle, UserProfile
from django.contrib.auth.models import User
from django.db import connection

def lab_hierarquia():
    org_uf, org_emp = load_mock_personas()
    
    # Reset queries para rastrear o que o ORM faz
    connection.queries_log.clear()

    # 1. Setup da Hierarquia
    depto, _ = Department.objects.get_or_create(organization=org_uf, slug="dcomp", defaults={"name": "Computação"})
    proj, _ = Project.objects.get_or_create(organization=org_uf, slug="ia-triagem", defaults={"name": "IA Triagem", "owner_department": depto})
    squad, _ = Squad.objects.get_or_create(project=proj, slug="modelagem", defaults={"name": "Modelagem"})

    # 2. Criação do Usuário
    prof, _ = User.objects.get_or_create(username="prof.ana", defaults={"email": "prof.ana@example.org"})
    UserProfile.objects.get_or_create(user=prof)

    # 3. Associação à Organização com Role
    role_org_member, _ = Role.objects.get_or_create(slug="org_member", defaults={"name": "Org Member", "scope": Role.Scope.ORGANIZATION})
    job_prof, _ = JobTitle.objects.get_or_create(name="Professor", level=Role.Scope.ORGANIZATION)
    org_membership, _ = OrganizationMembership.objects.get_or_create(
        organization=org_uf, 
        user=prof, 
        defaults={
            "role": role_org_member, 
            "job_title": job_prof
        }
    )

    print("--- Hierarquia Criada ---")
    print(f"User: {prof.username} | Org: {org_uf.name} | JobTitle: {org_membership.job_title}")
    
    # Imprime os SQLs executados
    print("\n--- SQL Equivalente (Principais) ---")
    for q in connection.queries[-3:]:
        print(q['sql'])

if __name__ == '__main__':
    run_lab(lab_hierarquia)
