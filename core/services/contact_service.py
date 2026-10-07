# core/services/contact_service.py | AI-Control SDD v0.6.0 | 29-09-2026 15:15(GMT-04:00)

import hashlib
from typing import Tuple, Optional
from core.models import Organization, Contact, ContactPhoneNumber, ContactOrganizationMembership
from core.utils import generate_phone_hash

class ContactService:
    @staticmethod
    def get_or_create_contact_for_webhook(
        sender_phone: str, 
        sender_jid: str, 
        push_name: str, 
        organization_slug: str = 'default'
    ) -> Tuple[Contact, Organization]:
        """
        Localiza (ou cria) um Contact e vincula a uma Organization de forma isolada.
        Utiliza o Blind Indexing para busca exata do telefone criptografado.
        """
        # Garante que a Organização existe (para o MVP, podemos usar 'default')
        org, _ = Organization.objects.get_or_create(
            slug=organization_slug,
            defaults={'name': 'Organização Default (Webhook)'}
        )
        
        phone_hash = generate_phone_hash(sender_phone)
        
        if not phone_hash:
            raise ValueError("O telefone fornecido não pôde ser limpo/hasheado.")

        # Busca pelo Hash (Postgres vai usar o índice btree)
        phone_obj = ContactPhoneNumber.objects.filter(phone_hash=phone_hash).first()
        
        if phone_obj:
            contact = phone_obj.contact
            # Atualiza o nome se estiver vazio e o push_name veio preenchido
            if not contact.full_name and push_name:
                contact.full_name = push_name
                contact.save()
        else:
            # Novo Contato
            contact = Contact.objects.create(full_name=push_name)
            phone_obj = ContactPhoneNumber.objects.create(
                contact=contact,
                whatsapp_jid=sender_jid,
                phone_number=sender_phone, # Será criptografado pelo field, e o save() gerará o hash
            )
            
        # Garante a associação (Membership) do Lead com a Organização (Tenant)
        ContactOrganizationMembership.objects.get_or_create(
            contact=contact,
            organization=org
        )
        
        return contact, org
