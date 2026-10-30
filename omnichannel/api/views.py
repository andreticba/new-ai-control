# views.py | AI-Control Omnichannel v0.6.0 | 21-10-2026 00:00:00(GMT-04:00)
import logging
import uuid
from django.db import models
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import OrganizationMembership, Organization
from omnichannel.models import Conversation, Message, CopilotDraft
from omnichannel.api.serializers.read import (
    ConversationReadSerializer,
    MessageReadSerializer,
    CopilotDraftReadSerializer,
)
from omnichannel.api.serializers.write import (
    MessageCreateSerializer,
)
from omnichannel.services import (
    InstanceService,
    TakeoverService,
    MessageDispatchService,
    EvolutionAPIException,
)

logger = logging.getLogger(__name__)


def _get_user_authorized_org_ids(user):
    """
    Retorna os IDs de organizações aos quais o usuário tem acesso.
    Superusuários, staff e perfis com plataforma ativa têm acesso global.
    """
    if user.is_superuser or user.is_staff:
        return list(Organization.objects.values_list('id', flat=True))

    if hasattr(user, 'profile') and user.profile.platform_role_id:
        return list(Organization.objects.values_list('id', flat=True))

    return list(
        OrganizationMembership.objects.filter(
            user=user,
            is_active=True
        ).values_list('organization_id', flat=True)
    )


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestão de conversas omnichannel (WhatsApp Web Clone).
    Delega operações de transbordo e leitura para a camada de serviços (Service Layer).
    """
    serializer_class = ConversationReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        authorized_orgs = _get_user_authorized_org_ids(user)
        qs = Conversation.objects.filter(
            organization_id__in=authorized_orgs
        ).select_related('contact').prefetch_related('messages')

        # Filtro explícito por organização
        org_id_param = self.request.query_params.get('org_id')
        if org_id_param:
            try:
                org_uuid = uuid.UUID(str(org_id_param))
                qs = qs.filter(organization_id=org_uuid)
            except (ValueError, TypeError):
                pass

        # Filtro por status
        status_param = self.request.query_params.get('status')
        if status_param in Conversation.Status.values:
            qs = qs.filter(status=status_param)

        # Abas de filtro: all | unread | ai | mine | pinned
        filter_param = self.request.query_params.get('filter')
        if filter_param == 'unread':
            qs = qs.filter(unread_count__gt=0)
        elif filter_param == 'ai':
            qs = qs.filter(status=Conversation.Status.ACTIVE_AI)
        elif filter_param == 'mine':
            qs = qs.filter(assigned_user_id=user.id)
        elif filter_param == 'pinned':
            qs = qs.filter(is_pinned=True)

        # Busca textual (nome do contato, preview da mensagem ou tags)
        search_param = self.request.query_params.get('search')
        if search_param:
            qs = qs.filter(
                models.Q(contact__whatsapp_push_name__icontains=search_param) |
                models.Q(last_message_preview__icontains=search_param) |
                models.Q(tags__contains=[search_param])
            )

        return qs.order_by('-is_pinned', '-last_message_timestamp')

    @action(detail=True, methods=['post'])
    def takeover(self, request, pk=None):
        """
        FR-004: Assumir atendimento humano (ACTIVE_HUMAN).
        Delega para TakeoverService com trava atômica e broadcast WebSocket.
        """
        conversation = self.get_object()
        updated_conv = TakeoverService.assign_to_human(conversation, request.user)
        serializer = self.get_serializer(updated_conv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='return-to-ai')
    def return_to_ai(self, request, pk=None):
        """
        FR-005: Devolver atendimento para a IA autônoma (ACTIVE_AI).
        Delega para TakeoverService.
        """
        conversation = self.get_object()
        updated_conv = TakeoverService.return_to_ai(conversation, request.user)
        serializer = self.get_serializer(updated_conv)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Marca todas as mensagens da conversa como lidas e zera o contador não lido.
        """
        conversation = self.get_object()
        TakeoverService.mark_as_read(conversation)
        return Response({"status": "success", "unread_count": 0})

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Retorna o histórico de mensagens da conversa com paginação e ordenação cronológica.
        """
        conversation = self.get_object()
        messages_qs = conversation.messages.select_related('quoted_message').order_by('timestamp')
        page = self.paginate_queryset(messages_qs)
        if page is not None:
            serializer = MessageReadSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageReadSerializer(messages_qs, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para mensagens e despacho outbound por operadores humanos.
    """
    serializer_class = MessageReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        authorized_orgs = _get_user_authorized_org_ids(user)
        qs = Message.objects.filter(
            conversation__organization_id__in=authorized_orgs
        ).select_related('quoted_message', 'conversation')

        conv_id = self.request.query_params.get('conversation_id')
        if conv_id:
            qs = qs.filter(conversation_id=conv_id)

        return qs.order_by('timestamp')

    def create(self, request, *args, **kwargs):
        """
        Envio de mensagem outbound por operador humano.
        Valida entrada via MessageCreateSerializer e delega para MessageDispatchService.
        """
        write_serializer = MessageCreateSerializer(data=request.data)
        if not write_serializer.is_valid():
            return Response(
                {"error": "Os campos 'conversation_id' e 'content' são obrigatórios.", "details": write_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = write_serializer.validated_data
        authorized_orgs = _get_user_authorized_org_ids(request.user)
        conversation = Conversation.objects.filter(
            id=data['conversation_id'],
            organization_id__in=authorized_orgs
        ).first()

        if not conversation:
            return Response(
                {"error": "Conversa não encontrada ou acesso não autorizado."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            msg = MessageDispatchService.send_operator_message(
                conversation=conversation,
                sender_user=request.user,
                content=data['content'],
                quoted_message_id=data.get('quoted_message_id'),
                media_type=data.get('media_type', Message.MediaType.TEXT),
                media_url=data.get('media_url'),
            )
            return Response(MessageReadSerializer(msg).data, status=status.HTTP_201_CREATED)
        except EvolutionAPIException as err:
            logger.error(f"[MessageViewSet] Falha ao despachar mensagem via Evolution API: {err}")
            return Response(
                {
                    "error": "Não foi possível enviar a mensagem no WhatsApp. A instância pode estar desconectada ou indisponível.",
                    "detail": str(err)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except ValueError as val_err:
            return Response({"error": str(val_err)}, status=status.HTTP_400_BAD_REQUEST)


class CopilotDraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet para as sugestões preditivas geradas pelo Copiloto de IA local.
    """
    serializer_class = CopilotDraftReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        authorized_orgs = _get_user_authorized_org_ids(user)
        return CopilotDraft.objects.filter(
            conversation__organization_id__in=authorized_orgs
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Aprova o draft sugerido pela IA e despacha como mensagem OUTBOUND via MessageDispatchService.
        """
        draft = self.get_object()
        if draft.status != CopilotDraft.Status.PENDING:
            return Response(
                {"error": f"Este draft já está no estado {draft.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        edited_content = request.data.get('edited_content', '').strip()
        final_content = edited_content if edited_content else draft.suggested_content

        conversation = draft.conversation
        quoted_id = draft.trigger_message.id if draft.trigger_message else None

        try:
            MessageDispatchService.send_operator_message(
                conversation=conversation,
                sender_user=request.user,
                content=final_content,
                quoted_message_id=quoted_id,
                sent_by_ai=True,
            )
        except EvolutionAPIException as err:
            logger.error(f"[CopilotDraftViewSet] Falha ao despachar draft aprovado: {err}")
            return Response(
                {
                    "error": "Não foi possível enviar a mensagem no WhatsApp. A instância pode estar desconectada.",
                    "detail": str(err)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except ValueError as val_err:
            return Response({"error": str(val_err)}, status=status.HTTP_400_BAD_REQUEST)

        draft.final_sent_content = final_content
        draft.status = CopilotDraft.Status.APPROVED
        draft.save(update_fields=['final_sent_content', 'status', 'updated_at'])

        return Response(self.get_serializer(draft).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def discard(self, request, pk=None):
        """
        Descarta o draft gerado pela IA.
        """
        draft = self.get_object()
        draft.status = CopilotDraft.Status.DISCARDED
        draft.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(draft).data, status=status.HTTP_200_OK)


class InstanceManageView(APIView):
    """
    Gestão de ciclo de vida da instância do WhatsApp na Evolution API.
    Delega integralmente para InstanceService.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _resolve_org(self, request):
        user = request.user
        authorized_orgs = _get_user_authorized_org_ids(user)
        req_org_id = request.headers.get('X-Organization-ID') or request.query_params.get('org_id')
        if req_org_id:
            try:
                org_uuid = uuid.UUID(str(req_org_id))
                if org_uuid in authorized_orgs or user.is_superuser:
                    return Organization.objects.filter(id=org_uuid).first()
            except (ValueError, TypeError):
                pass
        
        if hasattr(user, 'profile') and user.profile and user.profile.primary_organization_id in authorized_orgs:
            return user.profile.primary_organization
        if authorized_orgs:
            return Organization.objects.filter(id=authorized_orgs[0]).first()
        return None

    def get(self, request):
        org = self._resolve_org(request)
        if not org:
            return Response({"error": "Organização não localizada."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InstanceService.get_status(org.id))

    def post(self, request):
        org = self._resolve_org(request)
        if not org:
            return Response({"error": "Organização não localizada."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InstanceService.generate_qr(org.id, request=request))

    def delete(self, request):
        org = self._resolve_org(request)
        if not org:
            return Response({"error": "Organização não localizada."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InstanceService.disconnect(org.id, actor=request.user))
