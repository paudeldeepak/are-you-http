from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Post, Like
from django.utils.timezone import now

class LikeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an author
        self.author = Author.objects.create_user(
            username='authorusername',
            password='testpassword123',
            displayName='Author Name',
            github='http://github.com/authorname'
        )

        # Log in as the author for tests that require authentication
        self.client.force_authenticate(user=self.author)

        # Create a test post associated with the author
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='Test content',
            contentType='text/plain',
            visibility='PUBLIC',
            published=now()
        )

    def test_like_on_post_api(self):
        url = reverse('post_likes', args=[self.author.uid, self.post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.filter(post=self.post).count(), 1)

    def test_list_likes_on_post_api(self):
        # Create a like
        Like.objects.create(post=self.post, author=self.author)

        url = reverse('post_likes', args=[self.author.uid, self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

