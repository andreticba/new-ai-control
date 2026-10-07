import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import Role, Organization, UserProfile

@pytest.mark.django_db
class TestRBAC:
    def setup_method(self):
        self.org_a = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")
        
        self.user_a = User.objects.create_user(username="usera", password="123")
        self.user_a_profile = UserProfile.objects.create(user=self.user_a, primary_organization=self.org_a)
        
        self.user_b = User.objects.create_user(username="userb", password="123")
        self.user_b_profile = UserProfile.objects.create(user=self.user_b, primary_organization=self.org_b)
        
        # Give usera admin role
        role_admin = Role.objects.create(name="ADMIN")
        self.user_a_profile.roles.add(role_admin)
        
        # Give userb participant role
        role_part = Role.objects.create(name="PARTICIPANT")
        self.user_b_profile.roles.add(role_part)
        
        self.factory = RequestFactory()

    def test_gateway_access_admin_same_org(self):
        from core.middleware import rbac_middleware
        # Dummy view
        def dummy_view(request):
            return "OK"
            
        request = self.factory.get('/api/v1/gateway/')
        request.user = self.user_a
        
        response = rbac_middleware(dummy_view)(request)
        assert response == "OK"

    def test_gateway_access_participant_denied(self):
        from core.middleware import rbac_middleware
        def dummy_view(request):
            return "OK"
            
        request = self.factory.get('/api/v1/gateway/')
        request.user = self.user_b
        
        response = rbac_middleware(dummy_view)(request)
        assert response.status_code == 403
        
        from core.models import AuditLog
        assert AuditLog.objects.filter(action='FAILED_LOGIN').exists()
