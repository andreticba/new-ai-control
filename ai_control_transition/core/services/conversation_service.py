# core/services/conversation_service.py | AI-Control SDD v0.6.0 | 29-09-2026 15:18(GMT-04:00)

from core.models import Conversation, AuditLog
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    @staticmethod
    def assume_conversation(conversation_id: str, user: User) -> Conversation:
        """
        Altera o status da conversa para ACTIVE_HUMAN (Handoff),
        pausando a IA e registrando o evento no AuditLog.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise ValueError("Conversation not found")
            
        if conversation.status == Conversation.Status.ACTIVE_HUMAN:
            # Já está com um humano, talvez apenas reatribuindo
            pass
            
        conversation.status = Conversation.Status.ACTIVE_HUMAN
        conversation.assigned_user = user
        conversation.save(update_fields=['status', 'assigned_user', 'updated_at'])
        
        # Registrar o evento na Auditoria
        AuditLog.objects.create(
            actor=user,
            action=AuditLog.ActionType.HANDOFF_ASSUMED,
            target_contact=conversation.contact,
            target_content_type=ContentType.objects.get_for_model(Conversation),
            target_object_id=str(conversation.id),
            details={"previous_status": "ACTIVE_AI"}
        )
        
        logger.info(f"Handoff assumed by {user.username} for Conversation {conversation_id}")
        return conversation

    @staticmethod
    def return_to_ai(conversation_id: str, user: User) -> Conversation:
        """
        Retorna o controle da conversa para a Inteligência Artificial.
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise ValueError("Conversation not found")
            
        conversation.status = Conversation.Status.ACTIVE_AI
        conversation.assigned_user = None
        conversation.save(update_fields=['status', 'assigned_user', 'updated_at'])
        
        # Registrar o evento
        AuditLog.objects.create(
            actor=user,
            action=AuditLog.ActionType.UPDATE,
            target_contact=conversation.contact,
            target_content_type=ContentType.objects.get_for_model(Conversation),
            target_object_id=str(conversation.id),
            details={"event": "returned_to_ai"}
        )
        return conversation
