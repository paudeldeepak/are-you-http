from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Author, Friendship
from ..serializers import SignUpSerializer, SignInSerializer, AuthorSerializer

class SignupViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_success(self):
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'password': 'testpassword',
            'password2': 'testpassword',  # checks to see if matches password provided
            'displayName': 'New User',
            'github': 'http://github.com/newuser',
        }

        response = self.client.post(url, data, format='json')

        # Check if user is created successfully and a token is provided
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('data', response.data)


class SigninViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Author.objects.create_user(
            username='testuser',
            password='testpassword',
            displayName='Test User',
            github='http://github.com/testuser'
        )

    def test_signin_success(self):
       # Set the user to approved 
        self.user.is_approved = True
        self.user.save()

        url = reverse('signin')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        # Check for the presence of 'token' and 'data' when the user is approved
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('data', response.data)

        # Set the user to not approved for the second part of the test
        self.user.is_approved = False
        self.user.save()

        # Make the same request again and check for the absence of 'token' and 'data'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)
        self.assertNotIn('data', response.data)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Author is not approved', response.data['non_field_errors'])

class GetOneAuthorViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Author.objects.create_user(
            username='testuser',
            password='testpassword',
            displayName='Test User',
            github='http://github.com/testuser'
        )

    def test_get_one_author_success(self):
        url = reverse('getoneauthor', args=[str(self.user.uid)])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('uid', response.data)
        self.assertEqual(response.data['uid'], str(self.user.uid))


class DisplayAllAuthorsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Author.objects.create_user(
            username='testuser',
            password='testpassword',
            displayName='Test User',
            github='http://github.com/testuser'
        )

    def test_display_all_authors_success(self):
        url = reverse('displayallauthors')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('type', response.data)
        self.assertEqual(response.data['type'], 'authors')