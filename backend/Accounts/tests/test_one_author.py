
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Author, Friendship
from rest_framework.authtoken.models import Token
import base64

class GetOneAuthorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create_user(
            uid = '631f3ebe-d976-4248-a808-db2442a22168',
            username='will',
            password='testpass123',
            displayName='will',
            github='',
        )
        self.node = Author.objects.create_user(
            username = 'node',
            password = 'testpass123',
            displayName = 'node',
            github = '',
            is_approved = False,
            is_a_node = True,
        )
        self.url = reverse('getoneauthor', args=[self.author.uid])
        
    def test_get_one_author(self):
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        response = self.client.get(self.url)
        author = Author.objects.get(uid=self.author.uid)
        
        self.assertEqual(response.data['id'], self.author.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_author(self):
        data = {
            'displayName': 'will2',
        }
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        author1 = Author.objects.get(uid=self.author.uid)
        self.assertEqual(author1.displayName, data['displayName'])
        
        
    