# omnichannel/services/__init__.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:59:00(GMT-04:00)
"""
Service Layer do módulo Omnichannel.
Centraliza as operações de domínio, transbordo humano/IA, despacho outbound e ciclo de instâncias WhatsApp.
"""

from omnichannel.services.instance_service import InstanceService
from omnichannel.services.takeover_service import TakeoverService
from omnichannel.services.message_dispatch_service import MessageDispatchService, EvolutionAPIException
from omnichannel.services.default_organization_service import DefaultOrganizationService

__all__ = [
    'InstanceService',
    'TakeoverService',
    'MessageDispatchService',
    'EvolutionAPIException',
    'DefaultOrganizationService',
]
