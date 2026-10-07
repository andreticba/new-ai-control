# core/admin.py
from django.contrib import admin
from .models import (
    Permission, Role, Organization, Team, UserProfile, 
    ParticipantProfile, ConsentLog, Contact, ContactPhoneNumber, Conversation, Message
)

admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(Organization)
admin.site.register(Team)
admin.site.register(UserProfile)
admin.site.register(ParticipantProfile)
admin.site.register(ConsentLog)
admin.site.register(Contact)
admin.site.register(ContactPhoneNumber)
admin.site.register(Conversation)
admin.site.register(Message)
