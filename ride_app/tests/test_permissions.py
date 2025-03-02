from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from ride_app.permissions import IsAdminRole
from ride_app.models import User

class IsAdminRoleTest(TestCase):
    def setUp(self):
        self.permission = IsAdminRole()
        self.factory = APIRequestFactory()

        # Create an admin user.
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin',
            phone_number='1234567890'
        )
        # Create a non-admin user.
        self.non_admin_user = User.objects.create_user(
            username='user',
            password='password',
            first_name='Normal',
            last_name='User',
            email='user@example.com',
            role='customer',
            phone_number='0987654321'
        )

    def test_admin_has_permission(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        # view can be None since our permission doesn't use it.
        self.assertTrue(self.permission.has_permission(request, None))

    def test_non_admin_no_permission(self):
        request = self.factory.get('/')
        request.user = self.non_admin_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_anonymous_no_permission(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))
