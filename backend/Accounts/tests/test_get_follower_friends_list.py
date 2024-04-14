from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from ..models import Author, Friendship
from rest_framework.authtoken.models import Token

class FriendsAndFollowRequestsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create dummy authors
        self.author1 = Author.objects.create_user(username='author1', password='password123', displayName='Author One')
        self.author2 = Author.objects.create_user(username='author2', password='password123', displayName='Author Two')
        self.author3 = Author.objects.create_user(username='author3', password='password123', displayName='Author Three')

        # Get or create token for author1
        self.token, _ = Token.objects.get_or_create(user=self.author1)

        # Create friendships
        Friendship.objects.create(actor=self.author1, object=self.author2, status=3, summary='Author One is friends with Author Two')
        Friendship.objects.create(actor=self.author2, object=self.author1, status=3, summary='Author Two is friends with Author One')
        Friendship.objects.create(actor=self.author3, object=self.author1, status=1, summary='Author Three wants to follow Author One')

    def test_get_friends_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('displayallfriends', kwargs={'author_id': self.author1.uid}))
        print("Friends List:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  

    def test_get_follow_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(reverse('getfollowrequests', kwargs={'author_id': self.author1.uid}))
        print("Follow Requests:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Expecting 1 follow request (from author3)