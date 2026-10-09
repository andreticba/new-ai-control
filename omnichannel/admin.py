# omnichannel/admin.py | Atualizado em: 09-10-2026 19:46:00(GMT-04:00)
from django.contrib import admin
from .models import OmnichannelPreferences, Contact, ContactPhoneNumber, ContactOrganizationMembership, Conversation, Message

@admin.register(OmnichannelPreferences)
class OmnichannelPreferencesAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'reopen_conversation_timeout_hours', 'created_at', 'updated_at')
    search_fields = ('organization_id',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('full_name',)

@admin.register(ContactPhoneNumber)
class ContactPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_jid', 'contact', 'created_at')
    search_fields = ('whatsapp_jid',)

@admin.register(ContactOrganizationMembership)
class ContactOrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('contact', 'organization_id', 'created_at')
    search_fields = ('organization_id',)

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('direction', 'sender_whatsapp', 'content', 'sent_by_ai', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'contact', 'status', 'access_level', 'context_locked', 'current_intent', 'created_at')
    list_filter = ('status', 'access_level', 'context_locked')
    search_fields = ('organization_id', 'current_intent')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'direction', 'sender_whatsapp', 'sent_by_ai', 'sentiment', 'timestamp')
    list_filter = ('direction', 'sent_by_ai', 'visibility_level', 'sentiment')
    search_fields = ('content', 'sender_whatsapp', 'conversation__organization_id')
