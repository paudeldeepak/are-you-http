from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Author, Friendship
from rest_framework.authtoken.models import Token
import base64

class GetFollowersViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author1 = Author.objects.create_user(
            username='testuser1',
            password='testpass123',
            displayName='Test User 1',
            github='',
            is_approved=True,
        )
        self.author2 = Author.objects.create_user(
            username='testuser2',
            password='testpass123',
            displayName='Test User 2',
            github='',
            is_approved=True,
        )
        self.author3 = Author.objects.create_user(
            username='testuser3',
            password='testpass123',
            displayName='Test User 3',
            github='',
            is_approved=True,
        )
        self.author4 = Author.objects.create_user(
            username='testuser4',
            password='testpass123',
            displayName='Test User 4',
            github='',
            is_approved=True,
        )
        self.author5 = Author.objects.create_user(
            username='testuser5',
            password='testpass123',
            displayName='Test User 5',
            github='',
            is_approved=True,
        )

        # Check if a token already exists for author1
        if not Token.objects.filter(user=self.author1).exists():
            self.token1 = Token.objects.create(user=self.author1)

        # Check if a token already exists for author2
        if not Token.objects.filter(user=self.author2).exists():
            self.token2 = Token.objects.create(user=self.author2)

        # Check if a token already exists for author3
        if not Token.objects.filter(user=self.author3).exists():
            self.token3 = Token.objects.create(user=self.author3)

        # Check if a token already exists for author4
        if not Token.objects.filter(user=self.author4).exists():
            self.token4 = Token.objects.create(user=self.author4)

        # Check if a token already exists for author5
        if not Token.objects.filter(user=self.author5).exists():
            self.token5 = Token.objects.create(user=self.author5)
            
        else:
            self.token = Token.objects.get(user=self.author1)

        self.friendship1 = Friendship.objects.create(actor=self.author2, object=self.author1, status=2)
        self.friendship2 = Friendship.objects.create(actor=self.author3, object=self.author1, status=2)
        self.friendship3 = Friendship.objects.create(actor=self.author4, object=self.author1, status=2)
        self.friendship4 = Friendship.objects.create(actor=self.author5, object=self.author1, status=2)
        
    def test_get_followers_invalid_author_id(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        invalid_author_id = '00000000-0000-0000-0000-000000000000'  # An invalid UUID
        response = self.client.get(reverse('getfollowers', kwargs={'author_id': invalid_author_id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_followers(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('getfollowers', kwargs={'author_id': self.author1.uid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("List of followers:")
        for follower in response.data['items']:
            print(f"Username: {follower['username']}, DisplayName: {follower['displayName']}")
        print("." * 50)

    def test_get_followers_no_authentication(self):
        response = self.client.get(reverse('getfollowers', kwargs={'author_id': self.author1.uid}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_get_followers_no_followers(self):
        Friendship.objects.filter(object=self.author1).delete()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('getfollowers', kwargs={'author_id': self.author1.uid}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

    
    def test_get_followers_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid-token')
        response = self.client.get(reverse('getfollowers', kwargs={'author_id': self.author1.uid}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)