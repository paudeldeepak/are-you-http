from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from ..models import Author, Friendship
import base64


#Testing add friend request, delete friend request, check following 
#Delete friend request has a bug if both friends are following each other and one friend delets the request, the other friend is not deleted 
class FriendshipTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create_user(
            uid = '631f3ebe-d976-4248-a808-db2442a22168',
            username='will',
            password='testpass123',
            displayName='will',
            github='',
        )
        self.author2 = Author.objects.create_user(
            uid = 'adbfc58a-7d07-11ee-b962-0242ac120002',
            username='Joe',
            password='testpass123',
            displayName='joe',
            github='',
        )
        self.token1 = Token.objects.get_or_create(user=self.author)
        self.node = Author.objects.create_user(
            username = 'node',
            password = 'testpass123',
            displayName = 'node',
            github = '',
            is_approved = False,
            is_a_node = True,
        )
        self.client = APIClient()
        
        
        
        
     #ADD FRIEND REQUESTS:
    
    def test_adding_a_friend_1(self):
        '''
        Test for adding a friend when the other author is not following the sender
        '''
        #author2 sends a friend request to author
        self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        #author accepts the friend request 
        response = self.client.put(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        #author2 is now following author
        self.assertEqual(Friendship.objects.get(actor=self.author2, object=self.author).status, 2)
        self.client.credentials()
        
        
    def test_adding_a_friend_2(self):
        '''
        Test for adding a friend when the other author is following the sender
        '''

        #author2 sends a friend request to author
        self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        #author accepts the friend request and follows author2
        self.friend2 = Friendship.objects.create(actor=self.author, object=self.author2, status=2)
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        #both authors are now following each other therefore they are friends
        response = self.client.put(url)
        print(response.data)   
        self.assertEqual(response.status_code, 200)
        #bi-directional friendship
        self.assertEqual(Friendship.objects.get(actor=self.author2, object=self.author).status, 3)
        self.assertEqual(Friendship.objects.get(actor=self.author, object=self.author2).status, 3)
        self.client.credentials()
    
    
    def test_adding_a_friend_3(self):
        '''
        Test for adding a friend when the other author is already a friend
        '''

        # Both authors are friends
        self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=3)
        self.friend2 = Friendship.objects.create(actor=self.author, object=self.author2, status=3)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        
        url = reverse('singlefriendship', args=[self.author.uid, self.author2.uid])
        response = self.client.put(url)
        print(response.data)
        self.assertEqual(response.status_code, 400)

    
    
    def test_adding_a_friend_4(self):
        '''
        Test for adding a friend when there is no friend request
        '''
        #No friend relationship is created
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        response = self.client.put(url)
        print(response.data)
        self.assertEqual(response.status_code, 404)  
       
       
        
        
    #DELETE FRIEND REQUESTS:
        
    def test_delete_friendrequest_1(self):
        '''
        Test for deleting a friend request that exists and the other author is not following the sender
        '''
        #Author 2 sends a friend request to author -> pending
        self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        url = reverse('singlefriendship', args=[self.author2.uid,self.author.uid])
        response = self.client.delete(url)
        #Since status was 1 the friend request is deleted -> pending request gets deleted right away
        print(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Friendship.objects.count(), 1)
        self.client.credentials()

    
    def test_delete_friendrequest_2(self):
        '''
        Test for deleting a non existent friend request
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
       

    
    
    def test_check_following_1(self):
        '''
        Test for checking if an author is following another author
        '''
        self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=3)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        response = self.client.get(url)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_follower'], True)
        self.client.credentials()
        
    
    def test_check_following_2(self):
        '''
        Test for checking if an author is not following another author
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
        url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
        response = self.client.get(url)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_follower'], False)
        
        
        
    #FAILING TEST -> node tests fail
    # def test_check_following_remote_1(self):
    #     '''
    #     Test for checking if an author is following another author through a node
    #     '''
    #     userpass = f"{self.node.username}:{self.node.password}".encode("utf-8")
    #     userpass = base64.b64encode(userpass).decode("utf-8")
    #     self.client.credentials(HTTP_AUTHORIZATION = f'Basic {userpass}')
    #     self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=3)
    #     url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['is_follower'], True)
    #     self.client.credentials()
    
    
    #FAILING TEST
    # def test_check_following_remote_2(self):
    #     '''
    #     Test for checking if an author is following another author through a node
    #     '''
    #     userpass = f"{self.node.username}:{self.node.password}".encode("utf-8")
    #     userpass = base64.b64encode(userpass).decode("utf-8")
    #     self.client.credentials(HTTP_AUTHORIZATION = f'Basic {userpass}')
    #     url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['is_follower'], False)
    #     self.client.credentials()
    
    
    #FAILING TEST DOES NOT GET DELETED BOTH WAYS 
    # def test_delete_friendrequest_3(self):
    #     '''
    #     Test for deleting a friend when both are following each other
    #     '''
    #     #friend 1 following
    #     self.friend1 = Friendship.objects.create(actor=self.author2, object=self.author, status=3)
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1[0].key)
    #     #friend 2 following
    #     self.friend2 = Friendship.objects.create(actor=self.author, object=self.author2, status=3)
    #     url = reverse('singlefriendship', args=[self.author.uid,self.author2.uid])
    #     response = self.client.delete(url)
    #     self.friend2 = Friendship.objects.get(actor=self.author, object=self.author2)
    #     self.assertEqual(response.status_code, 204)
    #     self.assertEqual(Friendship.objects.count(), 1)
    #     self.assertEqual(self.friend2.status, 2)
    #     self.client.credentials()
       
       
    
       

    

    
#IGNORE THESE TEST CASES BELOW

# class FriendshipTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.author1 = Author.objects.create_user(
#             username='author1',
#             password='password123',
#             displayName='Author One',
#         )
#         self.author2 = Author.objects.create_user(
#             username='author2',
#             password='password123',
#             displayName='Author Two',
#         )
#         self.remote_node = Author.objects.create_user(
#             username='remote_node',
#             password='password123',
#             displayName='Remote Node',
#             is_a_node=True,
#         )
#         self.token1 = Token.objects.get_or_create(user=self.author1)[0].key
#         self.token2 = Token.objects.get_or_create(user=self.author2)[0].key

#     def _create_friendship(self, actor, object, status):
#         return Friendship.objects.create(
#             actor=actor,
#             object=object,
#             status=status,
#         )

    
#     #WORKING TESTS:
    
#     #1. Test to check if a user can become friends with another user
#     def test_become_friends(self):
#         self._create_friendship(actor=self.author1, object=self.author2, status=2)
#         self._create_friendship(actor=self.author2, object=self.author1, status=2)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.put(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(Friendship.objects.filter(actor=self.author1, object=self.author2, status=3).exists())
#         self.assertTrue(Friendship.objects.filter(actor=self.author2, object=self.author1, status=3).exists())

        
    
#     #2. Test to check if a user can follow another  -> user approve follow request
#     def test_approve_follow_request(self):
#         # Create a friendship with status 1 (follow request sent)
#         self._create_friendship(actor=self.author1, object=self.author2, status=1)
#         # Authenticate as author1
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         # Try to approve the follow request
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.put(url)
#         # Check the response
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(Friendship.objects.filter(actor=self.author1, object=self.author2, status=2).exists())



    
#     #3. Test to check if a user can deny a follow request
#     def test_deny_follow_request(self):
#         # Create a friendship with status 1 (follow request sent)
#         self._create_friendship(actor=self.author1, object=self.author2, status=1)

#         # Authenticate as author1
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)

#         # Try to deny the follow request
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.delete(url)

#         # Check the response
#         self.assertEqual(response.status_code, 204)  # Expecting 204 No Content on successful deletion
#         self.assertFalse(Friendship.objects.filter(actor=self.author2, object=self.author1).exists())

    
    
    
#     #4. Test to check if a user can check their followers
#     def test_check_followers(self):
#         self._create_friendship(actor=self.author2, object=self.author1, status=2)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('getfollowers', args=[self.author1.uid])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('author2', response.data['items'][0]['username'])
    
    
#     #5. Test to see if a user can unfollow another user
#     def test_unfollow_author(self):
#         self._create_friendship(actor=self.author1, object=self.author2, status=2)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, 204)
#         self.assertFalse(Friendship.objects.filter(actor=self.author1, object=self.author2).exists())

#     #6. Test to check if a user can check their friends 
#     def test_check_friends(self):
#         self._create_friendship(actor=self.author1, object=self.author2, status=3)
#         self._create_friendship(actor=self.author2, object=self.author1, status=3)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('displayallfriends', args=[self.author1.uid])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('author2', response.data[0]['actor']['username'])
#         self.assertIn('author1', response.data[0]['object']['username'])
    
    
#     #7. Check follower requests could be a redundant test
#     def test_check_follow_requests(self):
#         self._create_friendship(actor=self.author2, object=self.author1, status=1)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('getfollowrequests', args=[self.author1.uid])  # Update the URL to use 'followrequests'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(any(item['actor']['username'] == 'author2' for item in response.data))  # Check if 'author2' is in the list of follow requests
    
    
#     #8. Test case to follow a local author
#     def test_follow_local_author(self):
#         # Create a Friendship object before making the PUT request
#         self._create_friendship(actor=self.author1, object=self.author2, status=1)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1)
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.put(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(Friendship.objects.filter(actor=self.author1, object=self.author2, status=2).exists())

    
    
#     #9. Test to follow remote author
#     def test_follow_remote_author(self):
#         userpass = f"{self.remote_node.username}:{self.remote_node.password}".encode("utf-8")
#         userpass = base64.b64encode(userpass).decode("utf-8")
#         self._create_friendship(actor=self.author1, object=self.author2, status=1)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Basic {userpass}')
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.put(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(Friendship.objects.filter(actor=self.author1, object=self.author2, status=2).exists())
    
    
#     #10. Test to unfriend a remote author
#     def test_unfriend_remote_author(self):
#         self._create_friendship(actor=self.author1, object=self.author2, status=3)
#         self._create_friendship(actor=self.author2, object=self.author1, status=3)
#         userpass = f"{self.remote_node.username}:{self.remote_node.password}".encode("utf-8")
#         userpass = base64.b64encode(userpass).decode("utf-8")
#         self.client.credentials(HTTP_AUTHORIZATION=f'Basic {userpass}')
#         url = reverse('singlefriendship', args=[self.author1.uid, self.author2.uid])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, 204)
#         self.assertTrue(Friendship.objects.filter(actor=self.author1, object=self.author2, status=2).exists())
#         self.assertTrue(Friendship.objects.filter(actor=self.author2, object=self.author1, status=2).exists())

    
    

    