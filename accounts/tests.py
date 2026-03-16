import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, AuditLog


class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!@#',
            'password_confirm': 'StrongPass123!@#',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_register_password_mismatch(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!@#',
            'password_confirm': 'WrongPass123!@#',
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_email(self):
        User.objects.create_user(email='existing@example.com', username='existing', password='Pass123!@#')
        data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!@#',
            'password_confirm': 'StrongPass123!@#',
        }
        response = self.client.post('/api/v1/auth/register/', data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)


class TestUserLogin(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!@#',
        )

    def test_login_success(self):
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_login_wrong_password(self):
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'WrongPassword',
        }, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_login_creates_audit_log(self):
        self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#',
        }, format='json')
        self.assertTrue(AuditLog.objects.filter(user=self.user, action='login').exists())


class TestUserProfile(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!@#',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        response = self.client.patch('/api/v1/auth/profile/', {
            'first_name': 'Updated',
            'bio': 'Python developer',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_unauthenticated_profile_access(self):
        client = APIClient()
        response = client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserModel(TestCase):
    def test_execution_limit_free(self):
        user = User(role=User.Role.FREE)
        self.assertEqual(user.execution_limit, 50)

    def test_execution_limit_premium(self):
        user = User(role=User.Role.PREMIUM)
        self.assertEqual(user.execution_limit, 500)

    def test_can_execute_under_limit(self):
        user = User(role=User.Role.FREE, executions_today=10)
        self.assertTrue(user.can_execute)

    def test_cannot_execute_over_limit(self):
        user = User(role=User.Role.FREE, executions_today=50)
        self.assertFalse(user.can_execute)
