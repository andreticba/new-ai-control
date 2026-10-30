# test_extended_models.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:18:00(GMT-04:00)
import uuid
import pytest
from django.utils import timezone
from omnichannel.models import (
    Contact,
    ContactPhoneNumber,
    Conversation,
    Message,
    CopilotDraft,
)

@pytest.mark.django_db
class TestExtendedOmnichannelModels:

    def test_contact_with_avatar_and_push_name(self):
        contact = Contact.objects.create(
            full_name="Carlos Silva",
            whatsapp_push_name="Carlos WhatsApp",
            avatar_url="https://pps.whatsapp.net/v/t61.24694-24/avatar.jpg",
            status=Contact.Status.CLIENT,
        )
        assert contact.whatsapp_push_name == "Carlos WhatsApp"
        assert contact.avatar_url == "https://pps.whatsapp.net/v/t61.24694-24/avatar.jpg"
        assert contact.status == Contact.Status.CLIENT
        assert contact.id is not None

    def test_conversation_extended_fields(self):
        org_id = uuid.uuid4()
        contact = Contact.objects.create(
            whatsapp_push_name="Mariana Souza",
            status=Contact.Status.PROSPECT,
        )
        conv = Conversation.objects.create(
            contact=contact,
            organization_id=org_id,
            status=Conversation.Status.ACTIVE_AI,
            unread_count=3,
            last_message_preview="Olá, gostaria de saber os horários",
            is_pinned=True,
            channel_type=Conversation.ChannelType.WHATSAPP,
            instance_name="ai_control_clinica_sul",
            tags=["urgente", "consulta"],
        )
        
        assert conv.unread_count == 3
        assert conv.last_message_preview == "Olá, gostaria de saber os horários"
        assert conv.is_pinned is True
        assert conv.channel_type == "WHATSAPP"
        assert conv.instance_name == "ai_control_clinica_sul"
        assert conv.tags == ["urgente", "consulta"]

    def test_message_with_delivery_status_and_quoted_message(self):
        org_id = uuid.uuid4()
        contact = Contact.objects.create(status=Contact.Status.PLATFORM_LEAD)
        conv = Conversation.objects.create(contact=contact, organization_id=org_id)
        
        msg1 = Message.objects.create(
            conversation=conv,
            sender_whatsapp="5511999999999@s.whatsapp.net",
            direction=Message.Direction.INBOUND,
            content="Qual o valor da consulta?",
            external_id="EVO-MSG-001",
            delivery_status=Message.DeliveryStatus.DELIVERED,
            is_read=True,
            read_at=timezone.now(),
            media_type=Message.MediaType.TEXT,
            timestamp=timezone.now(),
        )
        
        attendant_id = uuid.uuid4()
        msg2 = Message.objects.create(
            conversation=conv,
            sender_whatsapp="ai_control_clinica",
            sender_user_id=attendant_id,
            direction=Message.Direction.OUTBOUND,
            content="O valor da primeira consulta é R$ 250,00.",
            external_id="EVO-MSG-002",
            delivery_status=Message.DeliveryStatus.READ,
            is_read=True,
            quoted_message=msg1,
            media_type=Message.MediaType.TEXT,
            timestamp=timezone.now(),
        )
        
        assert msg1.external_id == "EVO-MSG-001"
        assert msg1.delivery_status == Message.DeliveryStatus.DELIVERED
        assert msg2.quoted_message == msg1
        assert msg2.sender_user_id == attendant_id
        assert msg2.delivery_status == Message.DeliveryStatus.READ
        assert msg1.replies.count() == 1
        assert msg1.replies.first() == msg2

    def test_message_audio_rich_media(self):
        org_id = uuid.uuid4()
        contact = Contact.objects.create(status=Contact.Status.PLATFORM_LEAD)
        conv = Conversation.objects.create(contact=contact, organization_id=org_id)
        
        audio_msg = Message.objects.create(
            conversation=conv,
            sender_whatsapp="5511999999999@s.whatsapp.net",
            direction=Message.Direction.INBOUND,
            content="[Áudio]",
            media_type=Message.MediaType.AUDIO,
            media_url="https://s3.amazonaws.com/ai-control-media/audio_123.ogg",
            media_mimetype="audio/ogg; codecs=opus",
            media_duration=42,
            timestamp=timezone.now(),
        )
        
        assert audio_msg.media_type == "audio"
        assert audio_msg.media_duration == 42
        assert audio_msg.media_mimetype == "audio/ogg; codecs=opus"

    def test_copilot_draft_lifecycle(self):
        org_id = uuid.uuid4()
        contact = Contact.objects.create(whatsapp_push_name="Paciente Teste")
        conv = Conversation.objects.create(contact=contact, organization_id=org_id)
        
        trigger_msg = Message.objects.create(
            conversation=conv,
            sender_whatsapp="5511999999999@s.whatsapp.net",
            direction=Message.Direction.INBOUND,
            content="Vocês atendem Unimed?",
            timestamp=timezone.now(),
        )
        
        draft = CopilotDraft.objects.create(
            conversation=conv,
            trigger_message=trigger_msg,
            suggested_content="Sim, atendemos Unimed para diversas especialidades!",
            status=CopilotDraft.Status.PENDING,
            generated_by_model="phi4-mini:latest",
            latency_ms=312.5,
        )
        
        assert draft.id is not None
        assert draft.conversation == conv
        assert draft.trigger_message == trigger_msg
        assert draft.status == CopilotDraft.Status.PENDING
        assert draft.latency_ms == 312.5
        assert draft.generated_by_model == "phi4-mini:latest"
        
        # Simula aprovação humana com edição menor
        draft.final_sent_content = "Sim, atendemos o plano Unimed Clássico e Especial!"
        draft.status = CopilotDraft.Status.APPROVED
        draft.save()
        
        reloaded = CopilotDraft.objects.get(id=draft.id)
        assert reloaded.status == CopilotDraft.Status.APPROVED
        assert "Unimed Clássico" in reloaded.final_sent_content
