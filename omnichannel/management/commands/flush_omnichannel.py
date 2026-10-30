# flush_omnichannel.py | AI-Control Omnichannel v0.6.0 | 21-10-2026 13:10:00(GMT-04:00)
from django.core.management.base import BaseCommand
from django.db import transaction
from omnichannel.models import (
    Contact,
    ContactPhoneNumber,
    ContactOrganizationMembership,
    Conversation,
    Message,
    CopilotDraft,
)


class Command(BaseCommand):
    help = "Limpa completamente todos os dados do módulo Omnichannel (mensagens, conversas, drafts, telefones e contatos)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Confirma a deleção direta sem prompt interativo.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=== LIMPEZA TOTAL DE DADOS DO OMNICHANNEL ==="))

        counts = {
            "drafts": CopilotDraft.objects.count(),
            "messages": Message.objects.count(),
            "conversations": Conversation.objects.count(),
            "phones": ContactPhoneNumber.objects.count(),
            "memberships": ContactOrganizationMembership.objects.count(),
            "contacts": Contact.objects.count(),
        }

        self.stdout.write(
            f"Registros encontrados para deleção:\n"
            f" - CopilotDrafts: {counts['drafts']}\n"
            f" - Mensagens: {counts['messages']}\n"
            f" - Conversas: {counts['conversations']}\n"
            f" - Telefones (JIDs): {counts['phones']}\n"
            f" - Vínculos Organizacionais: {counts['memberships']}\n"
            f" - Contatos: {counts['contacts']}\n"
        )

        total_records = sum(counts.values())
        if total_records == 0:
            self.stdout.write(self.style.SUCCESS("O módulo Omnichannel já está completamente limpo!"))
            return

        if not options.get('yes'):
            confirm = input("Tem certeza que deseja apagar TODOS esses registros? (digite 'sim' para confirmar): ")
            if confirm.strip().lower() != 'sim':
                self.stdout.write(self.style.NOTICE("Operação cancelada pelo usuário."))
                return

        with transaction.atomic():
            # 1. Rascunhos de IA
            del_drafts, _ = CopilotDraft.objects.all().delete()
            # 2. Mensagens
            del_messages, _ = Message.objects.all().delete()
            # 3. Conversas (FK protegida para Contact)
            del_convs, _ = Conversation.objects.all().delete()
            # 4. Vínculos e Telefones
            del_memberships, _ = ContactOrganizationMembership.objects.all().delete()
            del_phones, _ = ContactPhoneNumber.objects.all().delete()
            # 5. Contatos
            del_contacts, _ = Contact.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("\n✅ Limpeza concluída com sucesso!"))
        self.stdout.write(
            f"Foram removidos:\n"
            f" - {del_drafts} rascunhos\n"
            f" - {del_messages} mensagens\n"
            f" - {del_convs} conversas\n"
            f" - {del_memberships} vínculos\n"
            f" - {del_phones} telefones\n"
            f" - {del_contacts} contatos\n"
        )
