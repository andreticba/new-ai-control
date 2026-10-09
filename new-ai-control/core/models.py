# models.py | Vitalia SDD v0.6.0 | 08-10-2026 19:56(GMT-04:00)
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import uuid
from .managers import TenantScopedManager

class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        ACCESS = 'ACCESS', _('Acesso a Dados')
        CREATE = 'CREATE', _('Criação')
        UPDATE = 'UPDATE', _('Atualização')
        DELETE = 'DELETE', _('Exclusão/Arquivamento')

    id = models.BigAutoField(primary_key=True)
    organization_id = models.UUIDField(null=True, blank=True, db_index=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ActionType.choices)
    
    target_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    target_object_id = models.CharField(max_length=255, null=True, blank=True)
    
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = TenantScopedManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"Audit: {self.action} by {self.actor} at {self.timestamp}"
