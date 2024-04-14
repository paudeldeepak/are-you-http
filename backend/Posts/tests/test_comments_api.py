from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Post, Comment
from django.utils.timezone import now

class CommentAPITests(TestCase):
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

    def test_create_comment_api(self):
        url = reverse('comments-post', args=[self.author.uid, self.post.id])
        data = {'comment': 'Test comment', 'contentType': 'text/plain', 'published': now()}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)

    def test_list_comments_api(self):
        # Create a comment
        Comment.objects.create(post=self.post, author=self.author, comment='Test comment', contentType='text/plain', published=now())

        url = reverse('comments-post', args=[self.author.uid, self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_comment_api(self):
        # Create a comment
        comment = Comment.objects.create(post=self.post, author=self.author, comment='Test comment', contentType='text/plain', published=now())

        url = reverse('comments-post', args=[self.author.uid, self.post.id, comment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Test comment')

    def test_update_comment_api(self):
        # Create a comment
        comment = Comment.objects.create(post=self.post, author=self.author, comment='Initial comment', contentType='text/plain', published=now())

        # Update the comment
        updated_comment = 'Updated comment'
        url = reverse('comments-post', args=[self.author.uid, self.post.id, comment.id])
        data = {'comment': updated_comment}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], updated_comment)

    def test_delete_comment_api(self):
        # Create a comment
        comment = Comment.objects.create(post=self.post, author=self.author, comment='Test comment', contentType='text/plain', published=now())

        url = reverse('comments-post', args=[self.author.uid, self.post.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)
