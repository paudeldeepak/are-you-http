import io
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Author
from PIL import Image


class SignupTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpass123'
        self.password2 = 'testpass123'
        self.wrongpassword2 = 'testpass1234'
        self.displayName = 'testuser'
        self.github = ''
        self.client = APIClient()

    def test_signup_correct(self):
        response = self.client.post(reverse('signup'), {'username': self.username, 'password': self.password, 'password2': self.password2, 'displayName': self.displayName, 'github': self.github})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Author.objects.filter(username=self.username).exists())

    def test_signup_wrongpassword(self):
        response = self.client.post(reverse('signup'), {'username': self.username, 'password': self.password, 'password2': self.wrongpassword2, 'displayName': self.displayName, 'github': self.github})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Author.objects.filter(username=self.username).exists())

    def test_signup_sameusername(self):
        self.client.post(reverse('signup'), {'username': self.username, 'password': self.password, 'password2': self.password2, 'displayName': self.displayName, 'github': self.github})
        response = self.client.post(reverse('signup'), {'username': self.username, 'password': self.password, 'password2': self.password2, 'displayName': self.displayName, 'github': self.github})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Author.objects.filter(username=self.username).count(), 1)

    def test_signup_withimage(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        response = self.client.post(reverse('signup'), {'username': self.username, 'password': self.password, 'password2': self.password2, 'displayName': self.displayName, 'github': self.github, 'profilePictureImage': file})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Author.objects.filter(username=self.username).exists())
