
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Author, Friendship
from rest_framework.authtoken.models import Token
import base64

class GetAllAuthorsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        for i in range(15):
            self.author = Author.objects.create_user(
                username=f'will{i}',
                password=f'testpass{i}',
                displayName=f'will{i}',
                github='',
                is_approved=True,
            )
        self.node = Author.objects.create_user(
            username = 'node',
            password = 'testpass123',
            displayName = 'node',
            github = '',
            is_approved = False,
            is_a_node = True,
        )
        
    
    def test_valid_pagination_authors(self):
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        response = self.client.get('/service/authors/',{'page': 1, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the expected keys
        self.assertIn('type', response.data)
        self.assertIn('items', response.data)
        self.assertIn('pagination', response.data)
        self.assertIn('next', response.data['pagination'])
        self.assertIn('previous', response.data['pagination'])
        self.assertIn('page_number', response.data['pagination'])
        self.assertIn('page_size', response.data['pagination'])

        # Check if the response has the correct number of items based on the provided page_size
        self.assertEqual(len(response.data['items']), 5)
        
    def test_default_pagination(self):
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        response = self.client.get('/service/authors/')
        # Check if the response has the expected status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the expected keys
        self.assertIn('type', response.data)
        self.assertIn('items', response.data)
        self.assertIn('pagination', response.data)
        self.assertIn('next', response.data['pagination'])
        self.assertIn('previous', response.data['pagination'])
        self.assertIn('page_number', response.data['pagination'])
        self.assertIn('page_size', response.data['pagination'])

        # Check if the response has the default number of items based on the default page_size
        self.assertEqual(len(response.data['items']), 15)
        
    def test_invalid_pagination(self):
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        # Make a GET request with invalid pagination parameters
        response = self.client.get('/service/authors/', {'page': 'invalid', 'page_size': 'invalid'})

        # Check if the response has the expected status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains the expected error message
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid page number or page size')