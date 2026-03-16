from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from .models import Snippet


class TestSnippetCRUD(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com', username='testuser', password='TestPass123!@#',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_snippet(self):
        data = {
            'title': 'Test Snippet',
            'code': 'print("hello")',
            'language': 'python',
            'visibility': 'public',
        }
        response = self.client.post('/api/v1/snippets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_snippets(self):
        Snippet.objects.create(user=self.user, title='Test', code='print(1)', share_slug='test1')
        response = self.client.get('/api/v1/snippets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_snippet(self):
        snippet = Snippet.objects.create(user=self.user, title='Test', code='print(1)', share_slug='test2')
        response = self.client.patch(f'/api/v1/snippets/{snippet.id}/', {'title': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_update_others_snippet(self):
        other_user = User.objects.create_user(email='other@example.com', username='other', password='Pass123!@#')
        snippet = Snippet.objects.create(user=other_user, title='Other', code='x=1', visibility='public', share_slug='test3')
        response = self.client.patch(f'/api/v1/snippets/{snippet.id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_star_snippet(self):
        snippet = Snippet.objects.create(user=self.user, title='Test', code='print(1)', visibility='public', share_slug='test4')
        response = self.client.post(f'/api/v1/snippets/{snippet.id}/star/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fork_snippet(self):
        snippet = Snippet.objects.create(user=self.user, title='Original', code='print(1)', visibility='public', share_slug='test5')
        response = self.client.post(f'/api/v1/snippets/{snippet.id}/fork/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Fork of Original', response.data['title'])
