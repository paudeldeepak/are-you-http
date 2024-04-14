from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import *
from django.contrib.auth.models import User

class CommentLikesAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        #create a test author
        self.author = Author.objects.create(
            username='testuser',
            password='testpassword',
            displayName='Test User',
            github='http://github.com/testuser'
        )

        #token for the test author
        self.token, created = Token.objects.get_or_create(user=self.author)

        #credentials for authentication
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        #test post
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='This is a test post content.',
            contentType='text/plain',
            visibility='PUBLIC',
            published=now()
        )

        #test comment associated with the test post
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            comment='Test Comment',
            contentType='text/plain',
            published=now()
        )

        #test like associated with the test comment
        self.like = Like.objects.create(
            comment=self.comment,
            author=self.author,
            published=now()
        )

        #URL for testing
        self.url = reverse('posts:comment_likes', kwargs={'author_id': str(self.author.id), 'post_id': str(self.post.id), 'comment_id': str(self.comment.id)})

    def test_get_likes_for_comment(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_likes_for_nonexistent_comment(self):
        url = reverse('posts:comment_likes', kwargs={'author_id': self.author.id, 'post_id': self.post.id, 'comment_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)