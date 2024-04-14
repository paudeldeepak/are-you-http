
import io
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Author
from PIL import Image


class SigninTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.displayName = 'testuser'
        self.github = ''
        self.client = APIClient()
        # Create a user for testing signin
        Author.objects.create_user(username=self.username, password=self.password, displayName=self.displayName, github=self.github, is_approved=True)

    def test_signin_correct(self):
        response = self.client.post(reverse('signin'), {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_signin_wrong_password(self):
        response = self.client.post(reverse('signin'), {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)

    def test_signin_nonexistent_user(self):
        response = self.client.post(reverse('signin'), {'username': 'nonexistentuser', 'password': 'password'})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)