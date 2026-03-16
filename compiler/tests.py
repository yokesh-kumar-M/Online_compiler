import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User


class TestFrontendViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Online Compiler')

    def test_run_code_no_code(self):
        response = self.client.post('/run/', {'code': ''})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])

    def test_validate_valid_code(self):
        response = self.client.post('/validate/', {'code': 'print("hello")'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['valid'])

    def test_validate_invalid_code(self):
        response = self.client.post('/validate/', {'code': 'def foo(:'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])

    def test_examples_endpoint(self):
        response = self.client.get('/examples/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('examples', data)


class TestCompilerAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!@#',
        )

    def test_execute_no_code(self):
        response = self.client.post('/api/v1/compiler/execute/', {'code': ''}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_execute_python_code(self):
        response = self.client.post(
            '/api/v1/compiler/execute/',
            {'code': 'print("hello")', 'language': 'python'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)

    def test_get_examples(self):
        response = self.client.get('/api/v1/compiler/examples/')
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get('/api/v1/compiler/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')

    def test_languages_endpoint(self):
        response = self.client.get('/api/v1/compiler/languages/')
        self.assertEqual(response.status_code, 200)
