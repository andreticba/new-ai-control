# models.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 18:37:00(GMT-04:00)
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

class OmnichannelPreferences(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(db_index=True, unique=True)
    reopen_conversation_timeout_hours = models.PositiveIntegerField(
        default=24,
        help_text=_("Tempo limite em horas para reabrir uma conversa antes de iniciar uma nova.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prefs for Org {self.organization_id}"

class Contact(models.Model):
    class Status(models.TextChoices):
        PLATFORM_LEAD = 'PLATFORM_LEAD', _('Lead da Plataforma')
        CUSTOMER_LEAD = 'CUSTOMER_LEAD', _('Lead de Cliente')
        PROSPECT = 'PROSPECT', _('Prospect')
        CLIENT = 'CLIENT', _('Cliente')
        ARCHIVED = 'ARCHIVED', _('Arquivado')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = EncryptedTextField(null=True, blank=True)
    search_tokens = ArrayField(models.CharField(max_length=32), blank=True, default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLATFORM_LEAD)
    
    # Extensões WhatsApp UI / PII (T001)
    avatar_url = models.TextField(null=True, blank=True)
    whatsapp_push_name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [GinIndex(fields=['search_tokens'], name='contact_name_blind_idx')]

    def save(self, *args, **kwargs):
        if self.full_name:
            try:
                from core.utils import generate_search_tokens
                self.search_tokens = generate_search_tokens(self.full_name)
            except Exception:
                pass
        else:
            self.search_tokens = []
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

class ContactPhoneNumber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='phone_numbers')
    
    whatsapp_jid = models.CharField(max_length=255, unique=True)
    
    phone_number = EncryptedCharField(max_length=50, null=True, blank=True)
    phone_hash = models.CharField(max_length=64, db_index=True, blank=True)

    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.phone_number:
            try:
                from core.utils import generate_phone_hash
                self.phone_hash = generate_phone_hash(self.phone_number)
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.whatsapp_jid

class ContactOrganizationMembership(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='memberships')
    organization_id = models.UUIDField(db_index=True)
    validated_email = EncryptedCharField(max_length=214, null=True, blank=True)
    notes = EncryptedTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        if 'organization' in kwargs:
            org = kwargs.pop('organization')
            kwargs['organization_id'] = org.id if hasattr(org, 'id') else org
        super().__init__(*args, **kwargs)

    @property
    def organization(self):
        if not self.organization_id:
            return None
        from core.models import Organization
        return Organization.objects.filter(id=self.organization_id).first()

    @organization.setter
    def organization(self, val):
        if val is None:
            self.organization_id = None
        elif hasattr(val, 'id'):
            self.organization_id = val.id
        else:
            self.organization_id = val

    class Meta:
        unique_together = ('contact', 'organization_id')

class Conversation(models.Model):
    class Status(models.TextChoices):
        ACTIVE_AI = 'ACTIVE_AI', _('Ativo (IA)')
        ACTIVE_HUMAN = 'ACTIVE_HUMAN', _('Ativo (Humano)')
        CLOSED = 'CLOSED', _('Fechado')

    class AccessLevel(models.TextChoices):
        PUBLIC = 'PUBLIC', _('Público')
        SUPERVISOR_ONLY = 'SUPERVISOR_ONLY', _('Apenas Supervisor')
        MUTED = 'MUTED', _('Silenciado')

    class ChannelType(models.TextChoices):
        WHATSAPP = 'WHATSAPP', _('WhatsApp')
        INSTAGRAM = 'INSTAGRAM', _('Instagram')
        TELEGRAM = 'TELEGRAM', _('Telegram')
        WEBCHAT = 'WEBCHAT', _('WebChat')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='conversations')
    organization_id = models.UUIDField(db_index=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE_AI)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.PUBLIC)
    
    assigned_user_id = models.UUIDField(db_index=True, null=True, blank=True)
    last_message_timestamp = models.DateTimeField(default=timezone.now)
    
    # Inteligência RAG (T007)
    context_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    current_intent = models.CharField(max_length=255, null=True, blank=True)
    consecutive_rag_failures = models.PositiveIntegerField(default=0)

    # Extensões WhatsApp UI / O(1) Performance (T002)
    unread_count = models.PositiveIntegerField(default=0)
    last_message_preview = models.TextField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    channel_type = models.CharField(max_length=20, choices=ChannelType.choices, default=ChannelType.WHATSAPP)
    instance_name = models.CharField(max_length=100, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        if 'organization' in kwargs:
            org = kwargs.pop('organization')
            kwargs['organization_id'] = org.id if hasattr(org, 'id') else org
        super().__init__(*args, **kwargs)

    @property
    def organization(self):
        if not self.organization_id:
            return None
        from core.models import Organization
        return Organization.objects.filter(id=self.organization_id).first()

    @organization.setter
    def organization(self, val):
        if val is None:
            self.organization_id = None
        elif hasattr(val, 'id'):
            self.organization_id = val.id
        else:
            self.organization_id = val

    @property
    def assigned_user(self):
        if not self.assigned_user_id:
            return None
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(id=self.assigned_user_id).first()

    @assigned_user.setter
    def assigned_user(self, val):
        if val is None:
            self.assigned_user_id = None
        elif hasattr(val, 'id'):
            self.assigned_user_id = val.id
        else:
            self.assigned_user_id = val

    def __str__(self):
        return f"{self.contact} - {self.status}"

class Message(models.Model):
    class Direction(models.TextChoices):
        INBOUND = 'INBOUND', _('Inbound')
        OUTBOUND = 'OUTBOUND', _('Outbound')

    class VisibilityLevel(models.TextChoices):
        PUBLIC = 'PUBLIC', _('Público')
        INTERNAL_TEAM = 'INTERNAL_TEAM', _('Equipe Interna')
        ARCHIVED = 'ARCHIVED', _('Arquivado')

    class Sentiment(models.TextChoices):
        NEUTRAL = 'NEUTRAL', _('Neutro')
        POSITIVE = 'POSITIVE', _('Positivo')
        URGENT = 'URGENT', _('Urgente')
        FRUSTRATED = 'FRUSTRATED', _('Frustrado')

    class DeliveryStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pendente')
        SENT = 'SENT', _('Enviado')
        DELIVERED = 'DELIVERED', _('Entregue')
        READ = 'READ', _('Lido')
        FAILED = 'FAILED', _('Falhou')

    class MediaType(models.TextChoices):
        TEXT = 'text', _('Texto')
        IMAGE = 'image', _('Imagem')
        AUDIO = 'audio', _('Áudio')
        VIDEO = 'video', _('Vídeo')
        DOCUMENT = 'document', _('Documento')
        STICKER = 'sticker', _('Sticker')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    sender_whatsapp = models.CharField(max_length=255)
    direction = models.CharField(max_length=20, choices=Direction.choices, default=Direction.INBOUND)
    content = models.TextField()
    
    sent_by_ai = models.BooleanField(default=False)
    visibility_level = models.CharField(max_length=20, choices=VisibilityLevel.choices, default=VisibilityLevel.PUBLIC)
    sentiment = models.CharField(max_length=20, choices=Sentiment.choices, default=Sentiment.NEUTRAL)

    # Extensões WhatsApp UI / Idempotência / Rich Media (T003)
    external_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.DELIVERED
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sender_user_id = models.UUIDField(db_index=True, null=True, blank=True)
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.TEXT
    )
    media_url = models.TextField(null=True, blank=True)
    media_mimetype = models.CharField(max_length=100, null=True, blank=True)
    media_duration = models.PositiveIntegerField(null=True, blank=True)
    quoted_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.direction}] {self.sender_whatsapp}"

class CopilotDraft(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendente')
        APPROVED = 'APPROVED', _('Aprovado')
        DISCARDED = 'DISCARDED', _('Descartado')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='copilot_drafts')
    trigger_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_drafts'
    )
    suggested_content = models.TextField()
    final_sent_content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    generated_by_model = models.CharField(max_length=100, default="phi4-mini:latest")
    latency_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft {self.id} for Conv {self.conversation_id} [{self.status}]"
