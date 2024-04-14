from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Author, Inbox_Feed, Post, Comment, Like, Friendship
from django.utils.timezone import now
import json

class InboxViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        #test user and auth
        self.author1 = Author.objects.create_user(
            username='authorusername',
            password='testpassword123',  
            displayName='Author Name',
            github='http://github.com/authorname'
        )
        self.author2 = Author.objects.create_user(
            username='authorusername2',
            password='testpassword1234',  
            displayName='Author Name2',
            github='http://github.com/authorname2'
        )
        
        self.client.force_authenticate(user=self.author1)

        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='This is a test post content.',
            contentType='text/plain',
            visibility='PUBLIC',
            published=now()
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author2,
            comment='This is a test comment.',
            contentType='text/plain',
            published=now()
        )
        self.like = Like.objects.create(
            post=self.post,
            author=self.author2,
            published=now()
        )  
        self.friendship = Friendship.objects.create(
            actor=self.author2, 
            object=self.author, 
            status=1
        ) 

        self.inbox_item = Inbox_Feed.objects.create(receiver=self.author2, sender=self.author1, post=self.post, comment=self.comment, like=self.like, friendship=self.friendship)

    def test_get_inbox(self):
        url = reverse('getinbox', kwargs={'author_id': self.author2.uid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_inbox(self):
        url = reverse('getinbox', kwargs={'author_id': self.author2.uid})
        data = {
            'type': 'Like',
            'object': self.post.id,  
            'author': {
                'id': str(self.author1.id),
            }
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
   

    def test_delete_inbox(self):
        url = reverse('getinbox', kwargs={'author_id': self.author2.uid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
