from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Like
from ..serializers import LikeSerializer

class AuthorLikedAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        #create author
        self.author = Author.objects.create_user(
            username='authorusername',
            password='testpassword123',
            displayName='Author Name',
            github='http://github.com/authorname',
            uid='4a36e3d1-95d4-4fd5-b857-4761cfde0cc5'
        )

        #authentication for author
        self.client.force_authenticate(user=self.author)

        #create likes associated with the author
        Like.objects.create(author=self.author)
        Like.objects.create(author=self.author)

        #URL for testing
        self.url = reverse('posts:author_likes', kwargs={'author_id': self.author.uid})

    def test_get_author_likes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #retrieve likes from the database
        author_likes = Like.objects.filter(author=self.author)
        serializer = LikeSerializer(author_likes, many=True)

        #check if response data matches the serialized data
        self.assertEqual(response.data['type'], 'liked')
        self.assertEqual(response.data['items'], serializer.data)