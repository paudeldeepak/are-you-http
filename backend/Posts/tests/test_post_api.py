from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Post, Author
from django.utils.timezone import now

class PostAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an author
        self.author = Author.objects.create_user(
            username='authorusername',
            password='testpassword123',  
            displayName='Author Name',
            github='http://github.com/authorname'
        )

        # Create a test post associated with the author
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='This is a test post content.',
            contentType='text/plain',
            visibility='PUBLIC',
            published=now()
        )

        self.client.force_authenticate(user=self.author)

        # Define URLs for testing 
        self.list_create_url = reverse('posts:author-posts', kwargs={'author_id': str(self.author.uid)})
        self.detail_url = reverse('posts:author-post', kwargs={'author_id': str(self.author.uid), 'post_id': self.post.pk})

    def test_get_post_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)
        
    def test_get_post_list_success(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.post.title)
    
    def test_get_post_not_found(self):
        response = self.client.get(reverse('posts:author-post', kwargs={'author_id': str(self.author.uid), 'post_id': 1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_post_update_unauthorized(self):
        data = {
            'title': 'Updated Post',
            'content': 'Updated post content',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_post_update_authorized(self):
        self.client.force_authenticate(user=self.author)
        data = {
            'title': 'Updated Post',
            'content': 'Updated post content',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
        }
        
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_unauthorized(self):
        data = {
            'title': 'New Post',
            'content': 'New post content',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_post_authorized(self):
        self.client.force_authenticate(user=self.author)
        data = {
            'title': 'New Post Auth',
            'content': 'Content for the new post',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)  # Original plus new post

    def test_delete_post_unauthorized(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_post_authorized(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_update_with_invalid_data(self):
        self.client.force_authenticate(user=self.author)
        data = {
            'title': '',  # Empty title is invalid
            'content': 'Updated post content',
            'contentType': 'text/plain',
            'visibility': 'PUBLIC',
        }

        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)  # Check if the error is about the title field