from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Organization

@receiver(post_save, sender=Organization)
def create_omnichannel_preferences(sender, instance, created, **kwargs):
    if created:
        try:
            from omnichannel.models import OmnichannelPreferences
            OmnichannelPreferences.objects.get_or_create(organization_id=instance.id)
        except Exception:
            pass
