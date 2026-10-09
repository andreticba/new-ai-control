import pytest
from core.models import Organization

@pytest.mark.django_db
def test_omnichannel_preferences_signal():
    # Este teste está vermelho até a criação do signal e do model OmnichannelPreferences
    from omnichannel.models import OmnichannelPreferences
    org = Organization.objects.create(name="Tenant Org")
    assert OmnichannelPreferences.objects.filter(organization_id=org.id).exists()
