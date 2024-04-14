from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Author, Post
from django.utils.timezone import now


class ImagePostAPITests(TestCase):
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

        # Create a test image post associated with the author
        base64_image = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAD/4QBGRXhpZgAATU0AKgAAAAgABwESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAA7aADAAQAAAABAAABPAAAAAD/2wBDAA...'

        self.image_post = Post.objects.create(
            author=self.author,
            title='Test Image Post',
            content=base64_image,
            contentType='image/jpeg;base64',
            visibility='PUBLIC',
            published=now()
        )

    def test_access_image_post(self):
        response = self.client.get(reverse('posts:serve-image-post', args=[self.author.uid, self.image_post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Type'].startswith('image/jpeg'))

    def test_access_friends_only_image_post_as_non_friend(self):
        # Create a friends-only post
        self.image_post.visibility = 'FRIENDS'
        self.image_post.save()

        # Create a user who is not a friend
        non_friend_user = Author.objects.create_user(username='nonfriend', password='pass123')

        # Authenticate as non-friend user
        self.client.force_authenticate(user=non_friend_user)

        # Attempt to access the friends-only post
        response = self.client.get(reverse('posts:serve-image-post', args=[self.author.uid, self.image_post.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)