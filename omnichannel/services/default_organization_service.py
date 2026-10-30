# omnichannel/services/default_organization_service.py | AI-Control SDD v0.6.0
import logging
import uuid
from typing import Optional
from django.conf import settings
from core.models import Organization

logger = logging.getLogger(__name__)


class DefaultOrganizationService:
    """
    Serviço canônico de governança para resolução e garantia da Organização Padrão.
    Assegura que contatos novos ou sem usuário sempre pertençam a uma Organização válida,
    impedindo organization_id nulo e preservando o isolamento multitenant (P01 & P07).
    """

    @classmethod
    def get_default_organization(cls) -> Organization:
        """
        Recupera ou cria de forma idempotente a Organização Padrão da plataforma.
        Ordem de resolução:
          1. settings.DEFAULT_ORGANIZATION_ID (se configurado e existente)
          2. Organização ativa com is_internal=True
          3. Organização ativa do tipo PLATFORM
          4. Primeira organização ativa do sistema
          5. Criação idempotente da organização interna padrão
        """
        # 1. Configuração explícita via settings / env
        default_org_id = getattr(settings, 'DEFAULT_ORGANIZATION_ID', None)
        if default_org_id:
            try:
                org_uuid = uuid.UUID(str(default_org_id))
                org = Organization.objects.filter(id=org_uuid, is_active=True).first()
                if org:
                    return org
            except (ValueError, TypeError):
                logger.warning(f"DEFAULT_ORGANIZATION_ID inválido: {default_org_id}")

        # 2. Organização interna da plataforma
        org = Organization.objects.filter(is_internal=True, is_active=True).first()
        if org:
            return org

        # 3. Organização do tipo PLATFORM
        org = Organization.objects.filter(org_type=Organization.OrgType.PLATFORM, is_active=True).first()
        if org:
            return org

        # 4. Primeira organização ativa disponível
        org = Organization.objects.filter(is_active=True).order_by('created_at').first()
        if org:
            return org

        # 5. Fallback atômico/idempotente: cria a organização padrão da plataforma
        org, _ = Organization.objects.get_or_create(
            is_internal=True,
            defaults={
                'name': 'Plataforma AI-Control',
                'org_type': Organization.OrgType.PLATFORM,
                'slug': 'platform',
                'is_active': True,
            }
        )
        return org
