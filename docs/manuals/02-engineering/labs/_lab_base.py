import os
import sys
import django
from django.db import transaction

# Ensure Django is set up
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_lab(lab_function):
    """
    Executa o laboratório isolado em uma transação com rollback garantido,
    para não poluir o banco de produção.
    """
    print(f"\n--- Iniciando Laboratório: {lab_function.__name__} ---")
    try:
        with transaction.atomic():
            lab_function()
            # Sempre lança exceção para garantir rollback
            raise Exception("Laboratório finalizado com sucesso. Acionando rollback para não poluir o banco.")
    except Exception as e:
        if str(e).startswith("Laboratório finalizado"):
            print(f"\n--- {e} ---")
        else:
            print(f"\n--- Erro no laboratório: {e} ---")
            import traceback
            traceback.print_exc()

def load_mock_personas():
    """
    Carrega as organizações base. Na realidade isso chamaria o 
    código de management command, mas para os labs criaremos as 
    necessidades pontuais.
    """
    from core.models import Organization
    org_uf, _ = Organization.objects.get_or_create(
        name="Universidade Federal Demo", 
        slug="ufdemo", 
        org_type=Organization.OrgType.ACADEMIC
    )
    org_emp, _ = Organization.objects.get_or_create(
        name="Empresa Demo Ltda", 
        slug="empresa-demo", 
        org_type=Organization.OrgType.COMPANY
    )
    return org_uf, org_emp
