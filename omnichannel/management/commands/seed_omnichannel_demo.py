# omnichannel/management/commands/seed_omnichannel_demo.py
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Organization
from omnichannel.models import (
    Contact,
    ContactPhoneNumber,
    ContactOrganizationMembership,
    Conversation,
    Message,
    CopilotDraft,
)


class Command(BaseCommand):
    help = "Popula o banco de dados com contatos, conversas e mensagens de demonstração para o Omnichannel."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando seed de demonstração do Omnichannel..."))

        org = Organization.objects.first()
        if not org:
            org = Organization.objects.create(
                name="Clínica Exemplo Matriz",
                slug="clinica-exemplo",
            )
            self.stdout.write(self.style.SUCCESS(f"Organização criada: {org.name} ({org.id})"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Usando organização existente: {org.name} ({org.id})"))

        # 1. Contatos e Telefones
        def get_or_create_contact(jid, full_name, avatar_url, status, notes):
            phone = ContactPhoneNumber.objects.filter(whatsapp_jid=jid).select_related('contact').first()
            if phone:
                c = phone.contact
                c.full_name = full_name
                c.avatar_url = avatar_url
                c.status = status
                c.whatsapp_push_name = full_name.split()[0]
                c.save()
            else:
                c = Contact.objects.create(
                    full_name=full_name,
                    avatar_url=avatar_url,
                    status=status,
                    whatsapp_push_name=full_name.split()[0],
                )
                phone = ContactPhoneNumber.objects.create(
                    contact=c,
                    whatsapp_jid=jid,
                    phone_number=jid.replace("@s.whatsapp.net", ""),
                )

            ContactOrganizationMembership.objects.update_or_create(
                contact=c,
                organization_id=org.id,
                defaults={"notes": notes},
            )
            return c

        contact1 = get_or_create_contact(
            jid="5511987654321@s.whatsapp.net",
            full_name="Dra. Ana Paula Ferreira",
            avatar_url="https://images.unsplash.com/photo-1594824813511-460f73f1d898?w=150&h=150&fit=crop&crop=face",
            status=Contact.Status.CLIENT,
            notes="Cliente corporativa do plano Premium. Atendimento prioritário.",
        )

        contact2 = get_or_create_contact(
            jid="5521998877665@s.whatsapp.net",
            full_name="Carlos Eduardo Lima",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            status=Contact.Status.PROSPECT,
            notes="Interessado na contratação do módulo de Telemedicina.",
        )

        contact3 = get_or_create_contact(
            jid="5531976543210@s.whatsapp.net",
            full_name="Mariana Vasconcelos",
            avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face",
            status=Contact.Status.CUSTOMER_LEAD,
            notes="Dúvida sobre reembolso de exames laboratoriais.",
        )

        # 2. Conversas
        # Conversa 1: ACTIVE_AI com Copilot Draft Pendente
        conv1, _ = Conversation.objects.update_or_create(
            organization_id=org.id,
            contact=contact1,
            defaults={
                "status": Conversation.Status.ACTIVE_AI,
                "channel_type": Conversation.ChannelType.WHATSAPP,
                "instance_name": f"ai_control_{org.slug or 'default'}",
                "is_pinned": True,
                "unread_count": 1,
                "tags": ["Cardiologia", "Prioritário"],
            },
        )

        # Mensagens da Conversa 1
        m1_1, _ = Message.objects.update_or_create(
            conversation=conv1,
            external_id="msg_demo_001",
            defaults={
                "direction": Message.Direction.INBOUND,
                "content": "Olá, gostaria de saber se meu laudo de ecocardiograma já está disponível no portal.",
                "sent_by_ai": False,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        m1_2, _ = Message.objects.update_or_create(
            conversation=conv1,
            external_id="msg_demo_002",
            defaults={
                "direction": Message.Direction.OUTBOUND,
                "content": "Olá Dra. Ana Paula! Estou verificando em nosso sistema integrado de laudos.",
                "sent_by_ai": True,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        m1_3, _ = Message.objects.update_or_create(
            conversation=conv1,
            external_id="msg_demo_003",
            defaults={
                "direction": Message.Direction.INBOUND,
                "content": "Perfeito, preciso dele até às 16h para a minha consulta de retorno.",
                "sent_by_ai": False,
                "delivery_status": Message.DeliveryStatus.DELIVERED,
                "is_read": False,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        # Copilot Draft para a mensagem 3
        CopilotDraft.objects.update_or_create(
            conversation=conv1,
            trigger_message=m1_3,
            defaults={
                "suggested_content": "Seu laudo de ecocardiograma já foi assinado digitalmente pelo médico responsável e liberado no portal! Você pode baixar pelo app ou clicar no link seguro: https://portal.clinica.exemplo/laudos/eco-123",
                "status": CopilotDraft.Status.PENDING,
                "generated_by_model": "phi4-mini:latest",
                "latency_ms": 115,
            },
        )

        # Conversa 2: ACTIVE_HUMAN (Operador assumiu)
        conv2, _ = Conversation.objects.update_or_create(
            organization_id=org.id,
            contact=contact2,
            defaults={
                "status": Conversation.Status.ACTIVE_HUMAN,
                "channel_type": Conversation.ChannelType.WHATSAPP,
                "instance_name": f"ai_control_{org.slug or 'default'}",
                "is_pinned": False,
                "unread_count": 0,
                "tags": ["Comercial", "Humano"],
            },
        )

        Message.objects.update_or_create(
            conversation=conv2,
            external_id="msg_demo_004",
            defaults={
                "direction": Message.Direction.INBOUND,
                "content": "Gostaria de agendar uma demonstração técnica da plataforma para a nossa equipe de enfermagem.",
                "sent_by_ai": False,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        Message.objects.update_or_create(
            conversation=conv2,
            external_id="msg_demo_005",
            defaults={
                "direction": Message.Direction.OUTBOUND,
                "content": "Boa tarde Carlos! Meu nome é Roberto e vou acompanhar o seu agendamento. Qual o melhor horário amanhã?",
                "sent_by_ai": False,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        # Conversa 3: CLOSED (Atendimento concluído)
        conv3, _ = Conversation.objects.update_or_create(
            organization_id=org.id,
            contact=contact3,
            defaults={
                "status": Conversation.Status.CLOSED,
                "channel_type": Conversation.ChannelType.WHATSAPP,
                "instance_name": f"ai_control_{org.slug or 'default'}",
                "is_pinned": False,
                "unread_count": 0,
                "tags": ["Suporte Concluído"],
            },
        )

        Message.objects.update_or_create(
            conversation=conv3,
            external_id="msg_demo_006",
            defaults={
                "direction": Message.Direction.INBOUND,
                "content": "Meu comprovante de reembolso foi aprovado?",
                "sent_by_ai": False,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        Message.objects.update_or_create(
            conversation=conv3,
            external_id="msg_demo_007",
            defaults={
                "direction": Message.Direction.OUTBOUND,
                "content": "Sim Mariana, o valor já foi creditado em sua conta cadastrada. Qualquer outra dúvida estamos à disposição!",
                "sent_by_ai": True,
                "delivery_status": Message.DeliveryStatus.READ,
                "is_read": True,
                "media_type": Message.MediaType.TEXT,
                "timestamp": timezone.now(),
            },
        )

        self.stdout.write(self.style.SUCCESS("✓ Seed de demonstração concluído com sucesso:"))
        self.stdout.write(f"  - 3 Contatos (Dra. Ana Paula, Carlos Eduardo, Mariana)")
        self.stdout.write(f"  - 3 Conversas (ACTIVE_AI com Copilot Draft, ACTIVE_HUMAN, CLOSED)")
        self.stdout.write(f"  - 7 Mensagens e 1 Sugestão do Copiloto")
