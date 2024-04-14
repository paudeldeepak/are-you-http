from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Post, Author
from django.contrib.auth.models import User

class SharePostWithFriendsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test author
        self.author = Author.objects.create(
            username='testuser',
            password='testpassword',
            displayName='Test Author',
            github='http://github.com/testauthor'
        )

        # Create a test post associated with the author
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='Test content',
            visibility='PUBLIC'
        )

    def test_share_post_with_friends(self):
        # Define the URL for sharing the post
        url = reverse('posts:share_with_friends', kwargs={'author_id': self.author.uid, 'post_id': self.post.id})

        # Make a POST request to share the post
        response = self.client.post(url)

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the post is shared with friends
        self.assertEqual(response.data['detail'], 'Post shared with friends.')

    def test_share_non_public_post_with_friends(self):
        # Change the post visibility to 'PRIVATE'
        self.post.visibility = 'PRIVATE'
        self.post.save()

        # Define the URL for sharing the post
        url = reverse('posts:share_with_friends', kwargs={'author_id': self.author.uid, 'post_id': self.post.id})

        # Make a POST request to share the post
        response = self.client.post(url)

        # Check that the response status code is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the error detail message is correct
        self.assertEqual(response.data['detail'], 'This post is not shared with friends.')