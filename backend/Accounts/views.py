import os
import random
from urllib.request import HTTPBasicAuthHandler
from django.shortcuts import get_object_or_404
import requests

from Social.models import ConnectedServer
from .serializers import *
from rest_framework import generics, status, permissions
from django.db import transaction
from rest_framework.response import Response
from Posts.utils import make_post_url
from backend.settings import HOST_URL
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from .models import *
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from .nodeAuthentication import NodesAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from Posts.serializers import PostSerializer, LikeSerializer, CommentCreateSerializer, CommentSerializer
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from django.db.models import Q
from requests.auth import HTTPBasicAuth
from rest_framework.exceptions import APIException
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from Posts.utils import make_comment_url
from urllib.parse import quote


# Generate a token for the user when they are created
logging.basicConfig(level=logging.INFO)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class TokenExchangeView(APIView):
    @swagger_auto_schema(
        operation_description="Exchange local token with remote token",
        responses={200: openapi.Response("Exchange successful"), 404: "Mapping not found"}
    )
    def get(self, request, remote_host):
        local_token = request.headers.get('Authorization').split(' ')[1]
        try:
            mapping = TokenMapping.objects.get(
                local_token=local_token, author__host=remote_host)
            return Response({'remote_token': mapping.remote_token}, status=status.HTTP_200_OK)
        except TokenMapping.DoesNotExist:
            return Response({'detail': 'Mapping not found'}, status=status.HTTP_404_NOT_FOUND)

########################################################################


# SIGNUP, SIGNIN, GETONEAUTHOR, DISPLAYALLAUTHORS.

class Signup(generics.CreateAPIView):
    # permission_classes = [AllowAny]
    serializer_class = SignUpSerializer
    @swagger_auto_schema(
    operation_description="Register a new user",
    responses={201: openapi.Response("User created successfully")},
)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            author = serializer.save()
            token, created = Token.objects.get_or_create(user=author)
            response = {
                'message': 'User created successfully',
                'token': token.key,
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Signin(generics.CreateAPIView):
    serializer_class = SignInSerializer
    @swagger_auto_schema(
    operation_description="Log in a user",
    responses={200: openapi.Response("User logged in successfully")},
)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            author = serializer.validated_data['author']
            token, created = Token.objects.get_or_create(user=author)
            response = {
                'message': 'User logged in successfully',
                'token': token.key,
                'data': author.uid
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Auth class is TokenAuthentication and  NodesAuthentication
@api_view(['GET', 'POST', 'PUT'])
@authentication_classes([TokenAuthentication, NodesAuthentication])
@permission_classes([permissions.IsAuthenticated])

def getOneAuthor(request, author_id):

    author = get_object_or_404(Author, uid=author_id)
    if request.method == 'GET':
        serializer = AuthorSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method in ['POST', 'PUT']:
        serializer = AuthorSerializer(
            instance=author, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Displays all authors in the database in a paginated manner
class DisplayAllAuthors(generics.CreateAPIView):
    pagination_class = PageNumberPagination
    serializer_class = AuthorSerializer
    # Auth class is TokenAuthentication and NodesAuthentication
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Display all approved authors",
        responses={200: AuthorSerializer(many=True), 400: "Invalid request"}
    )
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get(
            'page_size', self.pagination_class.page_size)
        try:
            page_number = int(page_number)
            page_size = int(page_size)
        except ValueError:
            return Response({'message': 'Invalid page number or page size'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Author.objects.filter(
            is_approved=True, is_a_node=False, is_remote=False, is_superuser=False).order_by('uid')
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuthorSerializer(
            page, many=True, context={'request': request})
        response = {
            "type": "authors",
            "items": serializer.data,
            'pagination': {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_number': page_number,
                'page_size': page_size,
            },
        }
        return Response(response, status=status.HTTP_200_OK)


########################################################################
class DisplayAllAuthorsOwn(generics.CreateAPIView):  # vs DisplayAllAuthors??
    pagination_class = PageNumberPagination
    serializer_class = AuthorSerializer
    # Auth class is TokenAuthentication and NodesAuthentication
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Display all approved authors",
        responses={200: AuthorSerializer(many=True), 400: "Invalid request"}
    )
    def get(self, request):
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get(
            'page_size', self.pagination_class.page_size)
        try:
            page_number = int(page_number)
            page_size = int(page_size)
        except ValueError:
            return Response({'message': 'Invalid page number or page size'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Author.objects.filter(
            is_approved=True, is_a_node=False, is_superuser=False).order_by('uid')
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuthorSerializer(
            page, many=True, context={'request': request})
        response = {
            "type": "authors",
            "items": serializer.data,
            'pagination': {
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_number': page_number,
                'page_size': page_size,
            },
        }
        return Response(response, status=status.HTTP_200_OK)


# GETFOLLOWERS, FRIENDSHIPVIEW, FRIENDSLISTVIEW, FOLLOWREQUESTVIEW

@swagger_auto_schema(
    operation_description="Send reverse friendship request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'remote_host': openapi.Schema(type=openapi.TYPE_STRING),
            'foreign_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'local_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'remote_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: "Reverse friendship request sent successfully", 400: "Invalid request"}
)

@method_decorator(csrf_exempt, name='dispatch')
def send_reverse_friendship_request(remote_host, foreign_author_id, local_author_id, remote_token):
    print("remote_host: follow", remote_host)
    print("foreign_author_id follow :", foreign_author_id)
    print("local_author_id: follow ", local_author_id)
    print("remote_token: follow", remote_token)

    url = f"{remote_host}authors/{local_author_id}/followers/{foreign_author_id}"
    print("URL:", url)
    headers = {"Authorization": f"Token {remote_token}"}
    try:
        response = requests.put(url, headers=headers)
        if response.status_code == 200:
            print("Reverse friendship request sent successfully")
            # Update the status of the original friendship to 'friends'
            original_friendship = Friendship.objects.filter(
                actor=local_author_id, object=foreign_author_id).first()
            reverse_friendship = Friendship.objects.filter(
                actor=foreign_author_id, object=local_author_id).first()
            if original_friendship and reverse_friendship:
                original_friendship.status = 3  # Assuming 3 represents 'friends'
                reverse_friendship.status = 3
                original_friendship.save()
                reverse_friendship.save()
                print("Friendship status updated to 'friends' for both sides")
            return True
        else:
            print(
                f"Failed to send reverse friendship request: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending reverse friendship request: {e}")
        return False

@swagger_auto_schema(
    operation_description="Send reverse unfollow request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'remote_host': openapi.Schema(type=openapi.TYPE_STRING),
            'local_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'foreign_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'remote_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: "Reverse unfollow request sent successfully", 400: "Invalid request"}
)
@method_decorator(csrf_exempt, name='dispatch')
def send_reverse_unfollow_request(remote_host, local_author_id, foreign_author_id, remote_token):
    print("remote_host unfollow:", remote_host)
    print("local_author_id unfollow:", local_author_id)
    print("foreign_author_id unfollow:", foreign_author_id)
    print("remote_token unfollow:", remote_token)

    # Note: The URL format should match the remote server's endpoint for unfollowing
    url = f"{remote_host}authors/{foreign_author_id}/followers/{local_author_id}"
    headers = {"Authorization": f"Token {remote_token}"}

    try:
        response = requests.delete(url, headers=headers)
        # Accept both 200 and 204 as success status codes
        if response.status_code in [200, 204]:
            print("Reverse unfollow request sent successfully")
            return True
        else:
            print(
                f"Failed to send reverse unfollow request: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending reverse unfollow request: {e}")
        return False

@swagger_auto_schema(
    operation_description="Send reverse deny request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'remote_host': openapi.Schema(type=openapi.TYPE_STRING),
            'local_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'foreign_author_id': openapi.Schema(type=openapi.TYPE_STRING),
            'remote_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={200: "Reverse deny request sent successfully", 400: "Invalid request"}
)
@method_decorator(csrf_exempt, name='dispatch')
def send_reverse_deny_request(remote_host, local_author_id, foreign_author_id, remote_token):
    print("remote_host deny:", remote_host)
    print("local_author_id deny:", local_author_id)
    print("foreign_author_id deny:", foreign_author_id)
    print("remote_token deny:", remote_token)

    # Note: The URL format should match the remote server's endpoint for denying a friend request
    url = f"{remote_host}authors/{foreign_author_id}/followers/{local_author_id}"
    # url = f"{remote_host}authors/{local_author_id}/followers/{foreign_author_id}"
    headers = {"Authorization": f"Token {remote_token}"}

    try:
        response = requests.delete(url, headers=headers)
        # Accept both 200 and 204 as success status codes
        if response.status_code in [200, 204]:
            print("Reverse deny request sent successfully")
            return True
        else:
            print(
                f"Failed to send reverse deny request: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending reverse deny request: {e}")
        return False


# Get all the authors that the user is following  and display them in a paginated manner
@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Get all the authors that the user is following",
    responses={200: AuthorSerializer(many=True), 400: "Invalid request"}
)
# Auth class is TokenAuthentication and NodesAuthentication
@authentication_classes([TokenAuthentication, NodesAuthentication])
@permission_classes([permissions.IsAuthenticated])
def getFollowers(request, author_id):
    author = get_object_or_404(Author, uid=author_id)
    followers = Friendship.objects.filter(object=author, status__in=[2, 3])
    followers = followers.values_list('actor', flat=True)
    followers = Author.objects.filter(uid__in=followers)
    serializer = AuthorSerializer(
        followers, many=True, context={'request': request})
    response = {
        "type": "followers",
        "items": serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class FriendshipView(generics.CreateAPIView):
    serializer_class = FriendsSerializer
    # Auth class is TokenAuthentication and NodesAuthentication
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete friendship",
        responses={204: "No content"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
            openapi.Parameter('foreign_author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Foreign Author ID"),
        ]
    )
    @method_decorator(csrf_exempt, name='dispatch')
    def delete(self, request, author_id, foreign_author_id):

        local_author = get_object_or_404(Author, uid=author_id)
        foreign_author = get_object_or_404(Author, uid=foreign_author_id)

        try:
            friendship = Friendship.objects.get(
                actor=foreign_author, object=local_author)
            is_foreign_author_actor = True
        except Friendship.DoesNotExist:

            friendship = get_object_or_404(
                Friendship, actor=local_author, object=foreign_author)
            is_foreign_author_actor = False

        if local_author.is_remote:
            remote_host = local_author.host
            remote_token = local_author.auth_token_key
            if friendship.status in [2, 3]:
                if not send_reverse_unfollow_request(remote_host, foreign_author_id, author_id, remote_token):
                    return Response({'message': 'Failed to unfollow remote user'}, status=status.HTTP_400_BAD_REQUEST)
            elif friendship.status == 1:
                if not send_reverse_deny_request(remote_host, foreign_author_id, author_id, remote_token):
                    return Response({'message': 'Failed to deny remote friend request'}, status=status.HTTP_400_BAD_REQUEST)

        elif foreign_author.is_remote and is_foreign_author_actor and friendship.status == 1:
            remote_host = foreign_author.host
            remote_token = foreign_author.auth_token_key
            if not send_reverse_deny_request(remote_host, author_id, foreign_author_id, remote_token):
                return Response({'message': 'Failed to deny remote friend request'}, status=status.HTTP_400_BAD_REQUEST)

        if not local_author.is_remote and not foreign_author.is_remote:
            if friendship.status in [2, 3]:
                reverse = Friendship.objects.filter(
                    actor=foreign_author, object=local_author).first()
                if reverse:
                    reverse.status = 2
                    reverse.save()
            elif friendship.status == 1:
                friendship.delete()
                return Response({'message': 'Follow request denied successfully'}, status=status.HTTP_204_NO_CONTENT)

        friendship.delete()
        return Response({'message': 'Friendship deleted'}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Update friendship status",
        responses={200: "Success", 400: "Bad request"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
            openapi.Parameter('foreign_author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Foreign Author ID"),
        ]
    )
    @method_decorator(csrf_exempt, name='dispatch')
    def put(self, request, author_id, foreign_author_id):
        author = get_object_or_404(Author, uid=author_id)
        foreign_author = get_object_or_404(Author, uid=foreign_author_id)

        print("Author:", author)
        print("Foreign Author:", foreign_author)

        friendship = Friendship.objects.filter(
            actor=foreign_author, object=author).first()

        print("Friendship:", friendship)

        if friendship and friendship.status == 1:
            print("Friendship exists and status is 1")
            friendship.status = 2
            friendship.save()

            if foreign_author.is_remote:
                print("Foreign author is remote")
                print("Foreign author host:", foreign_author.host)
                print("Foreign author token:", foreign_author.auth_token_key)
                print("Author id:", author_id)
                print("Foreign author id:", foreign_author_id)
                # Send reverse friendship request to remote server
                remote_host = foreign_author.host
                remote_token = foreign_author.auth_token_key
                if send_reverse_friendship_request(remote_host, foreign_author_id, author_id, remote_token):
                    print("Success - Reverse friendship request sent")
                else:
                    print("Failed to send reverse friendship request")
            else:
                reverse = Friendship.objects.filter(
                    actor=author, object=foreign_author).first()
                if reverse and reverse.status == 2:
                    print("Reverse friendship exists and status is 2")
                    friendship.status = 3
                    friendship.save()
                    reverse.status = 3
                    reverse.save()

            print("Success - Friendship updated")
            return Response({'message': 'Success'}, status=status.HTTP_200_OK)

        elif friendship and (friendship.status == 2 or friendship.status == 3):
            print("Already Friends")
            return Response({'message': 'Already Friends'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            print("No friend request has been sent")
            return Response({'message': 'No friend request has been sent'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Retrieve friendship status",
        responses={200: openapi.Response(description="Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
            openapi.Parameter('foreign_author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Foreign Author ID"),
        ]
    )
    def get(self, request, author_id, foreign_author_id):
        author = get_object_or_404(Author, uid=author_id)
        foreign_author = get_object_or_404(Author, uid=foreign_author_id)
        friendship = Friendship.objects.filter(
            actor=foreign_author, object=author, status__in=[2, 3]).first()
        if friendship:
            response_data = {
                "type": "Follow",
                "summary": "{} wants to follow {}".format(foreign_author.displayName, author.displayName),
                "actor": {
                    "type": "author",
                    "id": friendship.actor.id,
                    "url": friendship.actor.url,
                    "host": friendship.actor.host,
                    "displayName": friendship.actor.displayName,
                    "github": friendship.actor.github if friendship.actor.github is not None else "",
                    "profileImage": friendship.actor.profilePicture if friendship.actor.profilePicture is not None else ""
                },
                "object": {
                    "type": "author",
                    "id": friendship.object.id,
                    "host": friendship.object.host,
                    "displayName": friendship.object.displayName,
                    "url": friendship.object.url,
                    "github": friendship.object.github if friendship.object.github is not None else "",
                    "profileImage": friendship.object.profilePicture if friendship.object.profilePicture is not None else ""
                }
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)
        else:
            # retrurn a 404 if the user is not a follower
            return Response({'is_follower': False}, status=status.HTTP_404_NOT_FOUND)


class CheckFriendship(generics.CreateAPIView):

    @swagger_auto_schema(
        operation_description="Check pending friendships",
        responses={200: "Checked pending friendships"},
    )
    def post(self, request):
        print("Checking for foreign following")
        # get all the info from Friendship model
        friendship = Friendship.objects.all()

        # check if the status is pending
        pending = friendship.filter(status=1)

        print("Pending: ", pending)

        for i in pending:
            print("Checking for pending")
            if i.object.is_remote and "are-you-http" not in i.object.host:
                print("Checking for remote")
                # check if they have accepted the friend request
                node = get_object_or_404(ConnectedServer, host=i.object.host)
                actor_url_encoded = quote(i.actor.url, safe='')
                url = f"{node.api}authors/{i.object.uid}/followers/{actor_url_encoded}"
                
                print(actor_url_encoded)

                try:
                    response = requests.get(
                        url,
                        auth=HTTPBasicAuth(node.username, node.password),
                        headers={'Content-Type': 'application/json'}
                    )

                    # if the response is 200 then the user has accepted the friend request
                    if response.status_code == 200:
                        # changing the pending status to following
                        i.status = 2
                        i.save()

                except requests.exceptions.RequestException as e:
                    print("Request to {} failed: {}".format(url, e))

        return Response({"message": "Checked pending friendships"}, status=status.HTTP_200_OK)
    
class UpdateFriendshipFollowing(generics.CreateAPIView):
    # check if both user status is 2 and update it to 3
    @swagger_auto_schema(
        operation_description="Update friendships to following",
        responses={200: "Updated friendships"},
    )
    def post(self, request):
        print("Checking for foreign following")
        # get all the info from Friendship model
        friendship = Friendship.objects.all()

        # check if the status is following
        pending = friendship.filter(status=2)

        print("Following: ", pending)
        
        # if actor and object are both following each other, update status to 3
        for relation in pending:
            # Check if the reciprocal following exists
            if Friendship.objects.filter(actor=relation.object, object=relation.actor, status=2).exists():
                # Update the status to 3 for both relationships
                relation.status = 3
                relation.save()
                reciprocal_relation = Friendship.objects.get(actor=relation.object, object=relation.actor, status=2)
                reciprocal_relation.status = 3
                reciprocal_relation.save()

        return Response({"message": "Updated friendships"}, status=status.HTTP_200_OK)

class FriendsListView(generics.CreateAPIView):
    # Add node authentication later
    authentication_class = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of friends",
        responses={200: "List of friends"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def get(self, request, author_id):
        author = get_object_or_404(Author, uid=author_id)
        requests = Friendship.objects.filter(
            object=author, status=3) | Friendship.objects.filter(actor=author, status=3)
        serializer = FriendsSerializer(
            requests, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Issues with this not working properly
class FollowRequestView(generics.CreateAPIView):
    # Add node authentication later
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get pending follow requests",
        responses={200: "List of pending follow requests"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def get(self, request, author_id):
        # print("this is the author id: " + str(author_id))
        # print("this is the request: " + str(request))
        author = get_object_or_404(Author, uid=author_id)
        requests = Friendship.objects.filter(object=author, status=1)
        serializer = FriendsSerializer(
            requests, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Deny a follow request",
        responses={204: "Follow request denied"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
            openapi.Parameter('foreign_author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Foreign Author ID"),
        ]
    )
    def delete(self, request, author_id, foreign_author_id):
        author = get_object_or_404(Author, uid=author_id)
        foreign_author = get_object_or_404(Author, uid=foreign_author_id)

        try:
            # Get the follow request
            follow_request = Friendship.objects.get(
                object=author, status=1, actor=foreign_author)
        except Friendship.DoesNotExist:
            return Response({'message': 'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the follow request
        follow_request.delete()

        return Response({'message': 'Follow request denied successfully'}, status=status.HTTP_204_NO_CONTENT)


class PendingView(generics.CreateAPIView):
    # all the users the authors is attempting to follow
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get pending follow requests",
        responses={200: "List of pending follow requests"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def get(self, request, author_id):
        # print("this is the author id: " + str(author_id))
        # print("this is the request: " + str(request))
        author = get_object_or_404(Author, uid=author_id)
        requests = Friendship.objects.filter(actor=author, status=1)
        serializer = FriendsSerializer(
            requests, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingView(generics.CreateAPIView):
    # Add node authentication later
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get authors the user is following",
        responses={200: "List of authors the user is following"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def get(self, request, author_id):
        author = get_object_or_404(Author, uid=author_id)
        # Update this line to include status 3 as well
        following = Friendship.objects.filter(actor=author, status__in=[2, 3])
        serializer = FollowingSerializer(
            following, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


########################################################################
# INBOXVIEW


def generate_unique_username(base_username):
    while True:
        random_number = random.randint(1, 100000)
        username = f'{base_username}{random_number}'
        if not Author.objects.filter(username=username).exists():
            return username

# get all the inbox items for the user and display them in a paginated manner


@method_decorator(csrf_exempt, name='dispatch')
class InboxView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get inbox items",
        responses={200: "List of inbox items"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def get(self, request, author_id):
        """
        Get inbox items.

        :param request: HTTP request object.
        :param author_id: ID of the author whose inbox items are to be retrieved.
        :return: Response object.
        """
        receiver = get_object_or_404(Author, uid=author_id)
        inbox_items = Inbox_Feed.objects.filter(
            receiver=receiver).order_by('-published')
        itemList = []

        for item in inbox_items:
            itemData = {
                'sender_username': item.sender.username,
                'sender': item.sender.uid,  # include sender's uid?
                'link': item.link,
                'published': item.published,
            }
            # If there's a post associated, serialize it and include it in the response
            if item.post:
                post_serializer = PostSerializer(
                    item.post, context={'request': request})
                itemData['post'] = post_serializer.data
            if item.like:
                like_serializer = LikeSerializer(
                    item.like, context={'request': request})
                itemData['like'] = like_serializer.data
            if item.comment:
                comment_serializer = CommentSerializer(
                    item.comment, context={'request': request}
                )
                itemData['comment'] = comment_serializer.data

            itemList.append(itemData)

        response = {
            'type': 'inbox',
            'receiver': receiver.uid,
            'items': itemList
        }
        return Response(response, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Process requests for like, share, follow, or comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING, description="Request type (Like, post, Follow, comment)"),
                # Add other properties if needed
            }
        ),
        responses={201: "Request processed"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def post(self, request, author_id):
        """
        Process requests for like, share, follow, or comment.

        :param request: HTTP request object.
        :param author_id: ID of the author whose inbox items are to be retrieved.
        :return: Response object.
        """
        print(request.body)
        data = json.loads(request.body.decode('utf-8'))

        authorFilter = get_object_or_404(Author, uid=author_id)

        # Determine if the request is for a like or a share or a follow
        if 'type' in data and data['type'] == 'Like':
            return self.process_like(request, data, author_id)
        elif 'type' in data and data['type'] == 'post':
            return self.process_share(request, author_id)
        # Handle follow request
        elif 'type' in data and data['type'] == 'Follow':
            if authorFilter.is_remote:
                local_response = self.process_follow(request, author_id)
                if local_response.status_code != 201:
                    return local_response  # Return early if there was an issue processing locally
                # Then forward the request to the remote server
                return self.remoteProcessFollow(request, author_id)
            else:
                return self.process_follow(request, author_id)
        elif 'type' in data and data['type'] == 'comment':
            return self.process_comment(request, author_id)
        else:
            return JsonResponse({'message': 'Invalid request type'}, status=400)
        
    @swagger_auto_schema(
        operation_description="Clear inbox",
        responses={204: "Inbox cleared"},
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description="Author ID"),
        ]
    )
    def delete(self, request, author_id):
        """
        Clear inbox.

        :param request: HTTP request object.
        :param author_id: ID of the author whose inbox is to be cleared.
        :return: Response object.
        """
        receiver = get_object_or_404(Author, uid=author_id)

        # make sure the user is the receiver of the inbox items
        if request.user != receiver:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Delete all inbox items for the user
        inbox_items = Inbox_Feed.objects.filter(receiver=receiver)
        inbox_items.delete()

        return Response({'message': 'Inbox cleared'}, status=status.HTTP_204_NO_CONTENT)

    def remoteProcessFollow(self, request, author_id):
        # Decode JSON from the request body
        data = json.loads(request.body.decode('utf-8'))
        print("DATA: " + str(data))

        # Extract actor and object IDs from the data
        actor_data = data.get('actor')
        actor_uid = actor_data.get('id').split('/')[-1]

        object_data = data.get('object')
        object_id = object_data.get('id').split('/')[-1]

        # Retrieve Author instances based on extracted IDs
        actor = get_object_or_404(Author, uid=actor_uid)
        object_author = get_object_or_404(Author, uid=object_id)

        # Construct the payload to send
        follow_payload = {
            "type": "Follow",
            "summary": "{} wants to follow {}".format(actor.displayName, object_author.displayName),
            "actor": {
                "type": "author",
                "id": actor.id,
                "url": actor.url,
                "host": actor.host,
                "displayName": actor.displayName,
                "github": actor.github if actor.github is not None else "",
                "profileImage": actor.profilePicture if actor.profilePicture is not None else ""
            },
            "object": {
                "type": "author",
                "id": object_author.id,
                "url": object_author.url,
                "host": object_author.host,
                "displayName": object_author.displayName,
                "github": object_author.github if object_author.github is not None else "",
                "profileImage": object_author.profilePicture if object_author.profilePicture is not None else ""
            }
        }
        
        print("FOLLOW PAYLOAD: " + str(follow_payload))

        # Fetch connected server information
        authorFilter = get_object_or_404(Author, uid=author_id)
        node = get_object_or_404(ConnectedServer, host=authorFilter.host)
        url = node.api + 'authors/' + str(author_id) + '/inbox'

        # Send the POST request with the new payload
        response = requests.post(
            url,
            data=json.dumps(follow_payload),
            auth=HTTPBasicAuth(node.username, node.password),
            headers={'Content-Type': 'application/json'}
        )

        # Return the response as a JsonResponse
        return JsonResponse(response.json(), status=response.status_code, safe=False)

    def remoteProcess(self, request, author_id):
        print('In remote process')
        authorFilter = get_object_or_404(Author, uid=author_id)
        print(authorFilter)
        print(authorFilter.host)
        node = get_object_or_404(ConnectedServer, host=authorFilter.host)
        print("This is node" + str(node))
        print("This is node" + str(node.host))
        url = node.api + 'authors/' + str(author_id) + '/inbox'
        print("this is url: " + str(url))

        # Forward the request to the remote server
        response = requests.post(
            url,
            data=json.dumps(request.data),
            auth=HTTPBasicAuth(node.username, node.password),
            headers={'Content-Type': 'application/json'}
        )
        print(response.json())

        # Return the response from the remote server
        return JsonResponse(response.json(), status=response.status_code)

    def process_remote_comment(self, request, author_id):
        try:
            # Decode request body and load as JSON
            data = json.loads(request.body.decode('utf-8'))

            print("DATA: " + str(data))

            # Extract the sender's author information from the request data
            sender_data = data.get('author', {})

            print("SENDER DATA: " + str(sender_data))

            # Extract necessary information including comment ID from the URL
            comment_id_url = data.get('id')
            # Split the URL by slashes to access different parts of the path
            url_parts = comment_id_url.split('/')
            # Assuming the structure of the URL remains constant
            post_id = url_parts[-3]
            comment_id = url_parts[-1]

            print("POST ID: " + str(post_id))
            print("COMMENT ID: " + str(comment_id))

            sender_id = sender_data.get('id').split('/')[-1]
            comment_text = data.get('comment')
            content_type = data.get('contentType')
            published_date = data.get('published')

            print("SENDER ID: " + str(sender_id))
            print("COMMENT TEXT: " + str(comment_text))
            print("CONTENT TYPE: " + str(content_type))
            print("PUBLISHED DATE: " + str(published_date))
            print("COMMENT ID: " + str(comment_id))

            # Fetch the remote author instance
            sender_instance = get_object_or_404(Author, uid=sender_id)

            # Fetch the post object using the extracted post_id
            post = Post.objects.get(id=post_id)

            # Prepare data for the comment creation
            comment_data = {
                'id': comment_id,
                'comment': comment_text,
                'contentType': content_type,
                'published': published_date,
            }

            print("COMMENT DATA: " + str(comment_data))

            # update request user
            request.user = sender_instance

            # Use CommentSerializer to validate and save the comment data
            serializer = CommentCreateSerializer(
                data=comment_data, context={'request': request})
            if serializer.is_valid():
                print("SERIALIZER VALID")

                try:
                    serializer.save(author=sender_instance, post=post)
                except Exception as e:
                    print("Failed to save comment: " + str(e))
                    return JsonResponse({'message': 'Failed to save comment'}, status=500)

                # Fetch the receiver of the comment
                try:
                    print("RECEIVER ID: " + str(author_id))
                    receiver = Author.objects.get(uid=author_id)
                except Author.DoesNotExist:
                    print("Receiver not found")
                    return JsonResponse({'message': 'Receiver not found'}, status=404)

                try:
                    Inbox_Feed.objects.create(
                        receiver=receiver,
                        sender=sender_instance,
                        comment=serializer.instance
                    )
                except Exception as e:
                    print("Failed to add comment to inbox: " + str(e))
                    return JsonResponse({'message': 'Failed to add comment to inbox'}, status=500)

                print("COMMENT ADDED TO INBOX")

                return JsonResponse({'message': 'Remote comment processed and added to inbox successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Invalid data', 'errors': serializer.errors}, status=400)

        except Post.DoesNotExist:
            return JsonResponse({'message': 'Post not found'}, status=404)
        except Author.DoesNotExist:
            return JsonResponse({'message': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}'}, status=500)

    def process_comment(self, request, author_id):
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Extracting the sender's author information from the request data
            sender_data = data.get('author', {})
            print("SENDER DATA: " + str(sender_data))
            sender_id = sender_data.get('id').split('/')[-1]
            print("SENDER ID: " + str(sender_id))
            sender_instance = get_object_or_404(Author, uid=sender_id)

            if sender_instance.is_remote:
                return self.process_remote_comment(request, author_id)

            # Validate incoming data (assuming these are required fields)
            if not all(k in data for k in ('post_id', 'comment', 'contentType', 'type')):
                return JsonResponse({'message': 'Missing data for post_id, comment, contentType, or type'}, status=status.HTTP_400_BAD_REQUEST)

            post_id = data.get('post_id')

            comment_text = data.get('comment')
            content_type = data.get('contentType')
            request_type = data.get('type')

            # Fetch the post and author objects
            post = get_object_or_404(Post, id=post_id)
            author = get_object_or_404(Author, uid=author_id)

            # Prepare data for the comment creation
            comment_data = {
                'type': request_type,
                'comment': comment_text,
                'contentType': content_type,
            }

            # Use CommentCreateSerializer to validate and create the comment
            serializer = CommentCreateSerializer(
                data=comment_data, context={'request': request})
            if serializer.is_valid():
                comment = serializer.save(author=sender_instance, post=post)

                if author.is_remote:
                    # Forward the request to the remote server
                    node = get_object_or_404(ConnectedServer, host=author.host)
                    url = node.api + 'authors/' + str(author_id) + '/inbox'

                    # Serialize the comment object correctly
                    comment_serializer = CommentSerializer(
                        comment, context={'request': request})
                    serialized_data = comment_serializer.data

                    # Ensure the payload is correctly formatted for JSON
                    payload = json.dumps(serialized_data)

                    print("SERIALIZED Comment DATA: " + str(payload))

                    response = requests.post(
                        url,
                        data=payload,
                        auth=HTTPBasicAuth(node.username, node.password),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    # Handle the response
                    if response.status_code == 200:
                        return JsonResponse({'message': 'Comment forwarded successfully'}, status=200)
                    else:
                        # Logging or handling the failed response
                        return JsonResponse({'message': 'Failed to forward comment', 'details': response.json()}, status=response.status_code)
                else:
                    # Add the comment to the inbox of the receiving author
                    Inbox_Feed.objects.create(
                        receiver=author, sender=sender_instance, comment=comment)

                return JsonResponse({'message': 'Comment added to inbox successfully'}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_follow(self, request, author_id):
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("DATA: " + str(data))
            actor_data = data.get('actor')
            actor_uid = actor_data.get('id').split('/')[-1]

            object_data = data.get('object')
            obejct_id = object_data.get('id').split('/')[-1]

            actor = get_object_or_404(Author, uid=actor_uid)
            object = get_object_or_404(Author, uid=obejct_id)

            # Create or get the friendship from actor to object
            friendship, created = Friendship.objects.get_or_create(
                actor=actor,
                object=object,
                # Assuming 1 represents a follow request
                defaults={'status': 1}
            )

            # Add the follow request to the inbox if it's a new request
            if created:
                Inbox_Feed.objects.create(
                    receiver=object,
                    sender=actor,
                    friendship=friendship
                )
                return JsonResponse({'message': 'Friend request sent'}, status=201)
            else:
                return JsonResponse({'message': 'Follow request already exists'}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)

   

    def process_like(self, request, data, author_id):
        try:
            object_url = data.get('object')
            # Assuming object_id is the last part of the URL after the last '/'
            object_id = object_url.split('/')[-1]
            target_user = get_object_or_404(Author, uid=author_id)

            print("TARGET USER: " + str(target_user))

            # Determining if the like is for a post or a comment
            if "comments" in object_url:
                content_object = get_object_or_404(Comment, id=object_id)
            elif "posts" in object_url:
                content_object = get_object_or_404(Post, id=object_id)
            else:
                return JsonResponse({'message': 'Invalid object type'}, status=400)

            # Extracting the sender's author information from the request data
            sender_data = data.get('author', {})
            print("SENDER DATA: " + str(sender_data))
            sender_id = sender_data.get('id').split('/')[-1]
            print("SENDER ID: " + str(sender_id))
            sender_instance = get_object_or_404(Author, uid=sender_id)

            # Creating or getting the like instance
            like, created = Like.objects.get_or_create(
                author=sender_instance,
                post=content_object if isinstance(
                    content_object, Post) else None,
                comment=content_object if isinstance(
                    content_object, Comment) else None,
            )

            if target_user.is_remote:
                # Forward the request to the remote server
                node = get_object_or_404(
                    ConnectedServer, host=target_user.host)
                url = node.api + 'authors/' + str(author_id) + '/inbox'

                # serialize the like object
                like_serializer = LikeSerializer(
                    like, context={'request': request})
                serialized_data = like_serializer.data

                # payload is correctly formatted for JSON
                payload = json.dumps(serialized_data)

                response = requests.post(
                    url,
                    data=payload,
                    auth=HTTPBasicAuth(node.username, node.password),
                    headers={'Content-Type': 'application/json'}
                )

                # Handle response
                if response.status_code == 200:
                    return JsonResponse({'message': 'Like forwarded successfully'}, status=200)
                else:
                    return JsonResponse({'message': 'Failed to forward like'}, status=response.status_code)

            else:
                # Creating the inbox feed item
                Inbox_Feed.objects.create(
                    receiver=target_user,
                    sender=sender_instance,
                    like=like
                )
            if created:
                print("LIKE CREATED")
                return JsonResponse({'message': 'Like created successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Like already exists'}, status=200)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)

    def process_share(self, request, author_id):
        target_user_id = author_id
        # validate the target user - the person we want to share the post with
        target_user = get_object_or_404(Author, uid=target_user_id)

        if target_user.is_remote:
            node = get_object_or_404(ConnectedServer, host=target_user.host)
            url = node.api + 'authors/' + str(author_id) + '/inbox'
            # get the post id from the request data
            post_id = request.data.get('id').split('/')[-1]
            # get the post object
            post = get_object_or_404(Post, id=post_id)
            # send the post searalzied data to the remote server
            post_serializer = PostSerializer(
                post, context={'request': request})
            serialized_data = post_serializer.data
            print("SERIALIZED DATA: " + str(serialized_data))
            response = requests.post(
                url,
                data=json.dumps(serialized_data),
                auth=HTTPBasicAuth(node.username, node.password),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return JsonResponse({'message': 'Post shared successfully'}, status=200)
            else:
                return JsonResponse({'message': 'Failed to share post'}, status=response.status_code)

        # Extracting the sender's author information from the request data
        sender_data = request.data.get('author', {})
        print("SENDER DATA: " + str(sender_data))
        sender_id = sender_data.get('id').split('/')[-1]
        print("SENDER ID: " + str(sender_id))

        try:
            sender_instance = Author.objects.get(uid=sender_id)
        except Author.DoesNotExist:
            # if the person seding the post does not exist, create a new author object for them as they are remote
            sender_instance = Author.objects.create(
                uid=sender_id,
                id=sender_data.get('id'),
                username=sender_data.get('displayName'),
                password=sender_data.get(
                    'displayName') + str(random.randint(1, 100000)),
                displayName=sender_data.get('displayName'),
                github=sender_data.get('github'),
                host=sender_data.get('host'),
                url=sender_data.get('url'),
                profilePicture=sender_data.get('profileImage'),
                is_remote=True,
                is_active=True,
            )

        if sender_instance.is_remote:
            return self.process_remote_share(request, author_id)

        # get the post id from the request data
        post_id = request.data.get('id').split('/')[-1]

        # get the post object
        post = get_object_or_404(Post, id=post_id)

        # create an Inbox_Feed object to add this shared post to the target user's inbox
        inbox_item, created = Inbox_Feed.objects.update_or_create(
            receiver=target_user,
            sender=sender_instance,
            post=post,  # duplicate post sent to user's inbox
        )

        # Prepare the response
        if created:
            return Response({'message': 'Post shared successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Post already in the inbox.'}, status=status.HTTP_200_OK)

    def process_remote_share(self, request, author_id):
        # extract the shared post
        shared_post_data = request.data
        shared_post_author_data = shared_post_data.get('author', {})

        # retrieve the author instance or create a new one
        shared_post_author_id = shared_post_author_data.get(
            'id').split('/')[-1]

        try:
            shared_post_author = Author.objects.get(uid=shared_post_author_id)
        except Author.DoesNotExist:
            # create a new author object
            shared_post_author = Author.objects.create(
                uid=shared_post_author_id,
                id=shared_post_author_data.get('id'),
                username=shared_post_author_data.get('displayName'),
                password=shared_post_author_data.get(
                    'displayName') + str(random.randint(1, 100000)),
                displayName=shared_post_author_data.get('displayName'),
                github=shared_post_author_data.get('github'),
                host=shared_post_author_data.get('host'),
                url=shared_post_author_data.get('url'),
                profilePicture=shared_post_author_data.get('profileImage'),
                is_remote=True,
                is_active=True,
                is_approved=True,
            )

        # retrieve the shared post id
        shared_post_id = shared_post_data.get('id').split('/')[-1]

        # retrieve the shared post object
        try:
            shared_post = Post.objects.get(id=shared_post_id)
        except Post.DoesNotExist:
            # create a new post object

            # Check if the content is an image and missing the 'data:' prefix
            if shared_post_data.get('contentType') in ['image/png;base64', 'image/jpeg;base64'] and not shared_post_data.get('content').startswith('data:'):
                # Determine the correct MIME type to prepend
                mime_type = 'data:image/png;base64,' if shared_post_data.get(
                    'contentType') == 'image/png;base64' else 'data:image/jpeg;base64,'
                # Prepend the MIME type to the content
                shared_post_data['content'] = mime_type + \
                    shared_post_data.get('content')

            shared_post = Post.objects.create(
                id=shared_post_id,
                title=shared_post_data.get('title'),
                source=shared_post_data.get('source'),
                origin=shared_post_data.get('origin'),
                description=shared_post_data.get('description'),
                contentType=shared_post_data.get('contentType'),
                content=shared_post_data.get('content'),
                author=shared_post_author,
                visibility=shared_post_data.get('visibility'),
                published=shared_post_data.get('published'),
                id_url=shared_post_data.get('id'),
            )

        # retrieve the target user
        try:
            target_user = Author.objects.get(uid=author_id)
        except Author.DoesNotExist:
            return JsonResponse({'message': 'Author not found'}, status=404)

        # create an Inbox_Feed object to add this shared post to the target user's inbox
        Inbox_Feed.objects.create(  # create the inbox feed item
            receiver=target_user,
            sender=shared_post_author,
            post=shared_post,  # duplicate post sent to user's inbox
        )

        # get the comments url from the shared post data
        comments_url = shared_post_data.get('comments', None)

        # check if comments_url is a string
        if isinstance(comments_url, str):
            comments_url = comments_url
        else:
            comments_url = None

        # retrieve the comments for the shared post if the comments url is a string
        if comments_url:
            # get the node
            node = get_object_or_404(
                ConnectedServer, host=shared_post_author.host)
            # get the comments data from the remote server
            comments_request = requests.get(
                comments_url, auth=HTTPBasicAuth(node.username, node.password))
            if comments_request.status_code == 200:
                comments_data = comments_request.json().get('comments', [])
                print("COMMENTS DATA: " + str(comments_data))
                for comment_data in comments_data:
                    # extract the comment author data
                    comment_author_data = comment_data.get('author', {})
                    # retrieve the author instance or create a new one
                    comment_author_id = comment_author_data.get(
                        'id').split('/')[-1]
                    try:
                        comment_author = Author.objects.get(
                            uid=comment_author_id)
                    except Author.DoesNotExist:
                        # create a new author object
                        comment_author = Author.objects.create(
                            uid=comment_author_id,
                            id=comment_author_data.get('id'),
                            username=comment_author_data.get('displayName'),
                            password=comment_author_data.get(
                                'displayName') + str(random.randint(1, 100000)),
                            displayName=comment_author_data.get('displayName'),
                            github=comment_author_data.get('github'),
                            host=comment_author_data.get('host'),
                            url=comment_author_data.get('url'),
                            profilePicture=comment_author_data.get(
                                'profileImage'),
                            is_remote=True,
                            is_active=True,
                            is_approved = True,
                        )
                    # retrieve the comment id
                    comment_id = comment_data.get('id').split('/')[-1]
                    # retrieve the comment object
                    try:
                        comment = Comment.objects.get(id=comment_id)
                    except Comment.DoesNotExist:
                        # create a new comment object
                        comment = Comment.objects.create(
                            id=comment_id,
                            comment=comment_data.get('comment'),
                            contentType=comment_data.get('contentType'),
                            published=comment_data.get('published'),
                            author=comment_author,
                            post=shared_post,
                        )
                        comment_id_url = make_comment_url(comment.post.id_url,str(comment.id))
                        comment.id_url = comment_id_url
                        comment.save()

                        # check if comments has likes
                        # send a request to ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments/{COMMENT_ID}/likes
                        node = get_object_or_404(
                            ConnectedServer, host=comment_author.host)
                        likes_comment_url = f"{node.api}authors/{comment_author_id}/posts/{shared_post_id}/comments/{comment_id}/likes"

                        like_comments_request = requests.get(
                            likes_comment_url, auth=HTTPBasicAuth(node.username, node.password))
                        print("LIKE COMMENTS REQUEST: " + str(like_comments_request.json()))
                        if like_comments_request.status_code == 200:
                            likes_comment_data = like_comments_request.json()
                            for like_comment_data in likes_comment_data:
                                # extract the like author data
                                like_comment_author_data = like_comment_data.get(
                                    'author', {})
                                # retrieve the author instance or create a new one
                                like_comment_author_id = like_comment_author_data.get(
                                    'id').split('/')[-1]
                                try:
                                    like_comment_author = Author.objects.get(
                                        uid=like_comment_author_id)
                                except Author.DoesNotExist:
                                    # create a new author object
                                    like_comment_author = Author.objects.create(
                                        uid=like_comment_author_id,
                                        id=like_comment_author_data.get('id'),
                                        username=like_comment_author_data.get(
                                            'displayName'),
                                        password=like_comment_author_data.get(
                                            'displayName') + str(random.randint(1, 100000)),
                                        displayName=like_comment_author_data.get(
                                            'displayName'),
                                        github=like_comment_author_data.get(
                                            'github'),
                                        host=like_comment_author_data.get(
                                            'host'),
                                        url=like_comment_author_data.get(
                                            'url'),
                                        profilePicture=like_comment_author_data.get(
                                            'profileImage'),
                                        is_remote=True,
                                        is_active=True,
                                        is_approved=True,
                                    )
                                try:
                                    like_comment = Like.objects.get(
                                        author=like_comment_author, comment=comment)
                                except Like.DoesNotExist:
                                    # create a new like object
                                    like_comment = Like.objects.create(
                                        author=like_comment_author,
                                        comment=comment,
                                    )

        # check if the shared post has likes and add that as well
        # send a request to ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/likes
        node = get_object_or_404(
            ConnectedServer, host=shared_post_author.host)
        likes_url = f"{node.api}authors/{shared_post_author_id}/posts/{shared_post_id}/likes"
        likes_request = requests.get(
            likes_url, auth=HTTPBasicAuth(node.username, node.password))
        if likes_request.status_code == 200:
            likes_data = likes_request.json()
            for like_data in likes_data:
                # extract the like author data
                like_author_data = like_data.get('author', {})
                # retrieve the author instance or create a new one
                like_author_id = like_author_data.get('id').split('/')[-1]
                try:
                    like_author = Author.objects.get(uid=like_author_id)
                except Author.DoesNotExist:
                    # create a new author object
                    like_author = Author.objects.create(
                        uid=like_author_id,
                        id=like_author_data.get('id'),
                        username=like_author_data.get('displayName'),
                        password=like_author_data.get(
                            'displayName') + str(random.randint(1, 100000)),
                        displayName=like_author_data.get('displayName'),
                        github=like_author_data.get('github'),
                        host=like_author_data.get('host'),
                        url=like_author_data.get('url'),
                        profilePicture=like_author_data.get('profileImage'),
                        is_remote=True,
                        is_active=True,
                    )
                try:
                    like = Like.objects.get(
                        author=like_author, post=shared_post)
                except Like.DoesNotExist:
                    # create a new like object
                    like = Like.objects.create(
                        author=like_author,
                        post=shared_post,
                    )
        return Response({'message': 'Post shared successfully.'}, status=status.HTTP_201_CREATED)
########################################################################

# GETNODESVIEW


class GetNodesView(generics.CreateAPIView):
    serializer_class = AuthorSerializer

    @swagger_auto_schema(
        operation_description="Get all nodes",
        responses={200: openapi.Response("List of nodes")},
    )
    def get(self, request):
        """
        Get all nodes.

        :param request: HTTP request object.
        :return: Response object.
        """
        nodes = Author.objects.filter(is_a_node=True)
        serializer = AuthorSerializer(
            nodes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# NODE SETUP

class SetupNode(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Setup nodes",
        responses={200: openapi.Response("Setup complete")},
    )
    def get(self, request):
        """
        Setup nodes.

        :param request: HTTP request object.
        :return: Response object.
        """
        if not request.user or not request.user.is_a_node:
            return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        connected_servers = ConnectedServer.objects.all().filter(is_active=True)
        print(connected_servers)
        if not connected_servers:
            return Response({'message': 'No connected servers found'}, status=status.HTTP_404_NOT_FOUND)

        for server in connected_servers:
            try:
                name = server.username
                password = server.password
                remote_host = server.host
                remote_host_api = server.api

                if remote_host == "https://authcord1399-8a8b104296b1.herokuapp.com/":
                    author_request = requests.get(
                        f'{remote_host_api}authors/?page=1&size=100', auth=HTTPBasicAuth(name, password))
                else:
                    author_request = requests.get(
                        f'{remote_host_api}authors/', auth=HTTPBasicAuth(name, password))

                authors = author_request.json()['items']

                if 'are-you-http' not in remote_host:
                    print("Other Remote host: ", remote_host)
                    print("Local host: ", HOST_URL)
                    for author in authors:
                        author_uid = author['id'].split('/')[-1]
                        try:
                            author_obj = Author.objects.get(uid=author_uid)
                            logging.info(
                                f"Author already exists: {author_obj.displayName}")
                        except Author.DoesNotExist:
                            author_obj = Author.objects.create(
                                uid=author_uid,
                                username=author['displayName'] +
                                str(random.randint(1, 100000)),
                                password=author['displayName'] +
                                str(random.randint(1, 100000)),
                                displayName=author['displayName'],
                                github=author['github'],
                                host=author['host'],
                                id=author['id'],
                                url=author['url'],
                                profilePicture=author['profileImage'],
                                is_approved=True,
                                is_remote=True,

                            )
                            logging.info(
                                f"Created new author: {author_obj.displayName}")
                else:
                    for author in authors:
                        print("DO YOU EXIST", author)
                        try:
                            author_obj = Author.objects.get(uid=author['uid'])
                            logging.info(
                                f"Author already exists: {author_obj.displayName}")
                        except Author.DoesNotExist:
                            logging.info(f'creating author: {author['profileImage']}')
                            author_obj = Author.objects.create(
                                uid=author['uid'],
                                username=author['username'] +
                                str(random.randint(1, 100000)),
                                password=author['displayName'] +
                                str(random.randint(1, 100000)),
                                displayName=author['displayName'],
                                github=author['github'],
                                host=author['host'],
                                id=author['id'],
                                url=author['url'],
                                profilePicture=author['profileImage'],
                                is_approved=True,
                                is_remote=True,
                                auth_token_key=author['auth_token_key']
                            )
                            logging.info(
                                f"Created new author: {author_obj.displayName}")
                            # remote_token = tokens.get(author['uid'])
                            # TokenMapping.objects.update_or_create(
                            #     author=author_obj,
                            #     defaults={
                            #         'local_token': request.user.auth_token.key,
                            #         'remote_token': remote_token
                            #     }
                            # )
            except Exception as e:
                logging.error(
                    f"Error processing server {server.host}: {str(e)}")

        return Response({'message': 'Authors copied from connected servers'})
