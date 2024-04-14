from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Author, Comment, Like
from .serializers import PostSerializer, CommentSerializer, PostCreateSerializer, CommentCreateSerializer, LikeSerializer
from .utils import is_friend, make_comments_url, make_post_url
from .postShareFriends import send_post_to_friends, send_post_to_following
from .pagination import CommentPagination
from django.http import HttpResponse
import base64
from backend.settings import HOST_URL
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from Accounts.nodeAuthentication import NodesAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class AuthorPost(APIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, author_id, post_id, request_user):
        post = get_object_or_404(Post, pk=post_id, author_id=author_id)
        if post.visibility == 'PUBLIC' or post.visibility == 'UNLISTED':
            # Public and Unlisted posts are accessible to anyone who knows the URI.
            # Note: For UNLISTED, it's implicitly understood that it's accessible without further checks.
            return post
        elif post.visibility == 'FRIENDS':
            if request_user.is_authenticated:
                if request_user == post.author:
                    # This ensures the author can always see their own posts, regardless of visibility setting.
                    return post
                else:
                    if is_friend(request_user, post.author):
                        return post
            else:
                raise PermissionDenied(
                    "You do not have permission to view this post.")

    @swagger_auto_schema(
        operation_description="Retrieve, update, or delete a specific post by the author.",
        responses={200: PostSerializer(), 403: "Permission Denied", 404: "Not Found"},
    )

    def get(self, request, author_id, post_id):
        post = self.get_object(author_id, post_id, request.user)
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a specific post by the author.",
        request_body=PostSerializer(),
        responses={200: PostSerializer(), 400: "Bad Request", 403: "Permission Denied", 404: "Not Found"},
    )
    def put(self, request, author_id, post_id):
        post = self.get_object(author_id, post_id, request.user)
        if request.user != post.author:
            raise PermissionDenied(
                "You do not have permission to edit this post.")
        serializer = PostSerializer(
            post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a specific post by the author.",
        responses={204: "No Content", 403: "Permission Denied", 404: "Not Found"},
    )
    def delete(self, request, author_id, post_id):
        post = self.get_object(author_id, post_id, request.user)
        if request.user != post.author:
            raise PermissionDenied(
                "You do not have permission to delete this post.")
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthorPosts(APIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self, author_id, request_user):
        author = get_object_or_404(Author, uid=author_id)
        if request_user.is_authenticated:
            if request_user == author:
                return Post.objects.filter(author=author).order_by('-published')
            elif is_friend(request_user, author):
                # Friends can see public, friends-only, and unlisted posts
                return Post.objects.filter(author=author).exclude(visibility='UNLISTED').order_by('-published')
        # Default case for unauthenticated users or non-friends: only public posts
        return Post.objects.filter(author=author, visibility='PUBLIC').order_by('-published')

    @swagger_auto_schema(
        operation_description="Retrieve posts for a specific author.",
        responses={200: PostSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
    )
    def get(self, request, author_id):
        posts = self.get_queryset(author_id, request.user)
        serializer = PostSerializer(
            posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Create a post as author_id.",
        responses={201: 'Post Created', 400: 'Bad Request', 403: 'Permission Denied'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'description', 'contentType', 'content', 'visibility'],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING),
                "source": openapi.Schema(type=openapi.TYPE_STRING),
                "origin": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "contentType": openapi.Schema(type=openapi.TYPE_STRING),
                "content": openapi.Schema(type=openapi.TYPE_STRING),
                "visibility": openapi.Schema(type=openapi.TYPE_STRING, example="PUBLIC")
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
    )

    def post(self, request, author_id):
        # Use uid for UUID field
        author = get_object_or_404(Author, uid=author_id)
        if request.user != author:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        # Pass the request context when instantiating the serializer
        serializer = PostCreateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save(author=author)
            if post.visibility == 'FRIENDS':
                send_post_to_friends(request, author_id, post.id)
            if post.visibility == 'PUBLIC':
                # Send the post to the people that are following the author
                send_post_to_following(request, author_id, post.id)
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServeImagePost(APIView):
    # authentication_classes = [TokenAuthentication, NodesAuthentication]
    # permission_classes = [IsAuthenticated]
    def get_object(self, post_id, request_user):
        post = get_object_or_404(Post, pk=post_id)
        if post.visibility == 'PUBLIC' or post.visibility == 'UNLISTED':
            return post
        elif post.visibility == 'FRIENDS':
            if request_user.is_authenticated and is_friend(request_user, post.author):
                return post
            else:
                raise PermissionDenied(
                    "You do not have permission to view this post.")
        else:
            if request_user == post.author:
                return post
            else:
                raise PermissionDenied(
                    "You do not have permission to view this post.")

    @swagger_auto_schema(
        operation_description="Retrieve an image post.",
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'post_id',
                in_=openapi.IN_PATH,
                description='ID of a post',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
    )

    def get(self, request, author_id, post_id):
        post = self.get_object(post_id, request.user)

        if post.contentType in ['image/png;base64', 'image/jpeg;base64']:
            format, imgstr = post.content.split(
                ';base64,')  # format = data:image/png
            # Extracts the image format (png or jpeg)
            ext = format.split('/')[-1]

            # Ensure the base64 string has the correct padding
            # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
            padding = 4 - len(imgstr) % 4
            if padding:
                imgstr += "=" * padding

            image_data = base64.b64decode(imgstr)
            return HttpResponse(image_data, content_type="image/" + ext)
        else:
            raise PermissionDenied("The requested post is not an image.")


class PostComments(APIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination()

    def can_view_comments(self, post, request_user):
        """
        Determines if the request_user can view comments on the post.
        """
        if post.visibility == 'PUBLIC':
            return True
        elif request_user.is_authenticated:
            if post.author == request_user:
                return True
            elif post.visibility == 'FRIENDS' and is_friend(request_user, post.author):
                return True
        return False

    @swagger_auto_schema(
        operation_description="Retrieve comments for a specific post.",
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'post_id',
                in_=openapi.IN_PATH,
                description='ID of a post',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={200: CommentSerializer(many=True)},
    )

    def get(self, request, author_id, post_id):
        post = get_object_or_404(Post, id=post_id, author__uid=author_id)
        if not self.can_view_comments(post, request.user):
            return Response({"detail": "You do not have permission to view these comments."}, status=status.HTTP_403_FORBIDDEN)
        comments = Comment.objects.filter(post=post).order_by('-published')
        page = self.pagination_class.paginate_queryset(
            comments, request, view=self)
        if page is not None:
            serializer = CommentSerializer(
                page, many=True, context={'request': request})
            return self.get_custom_paginated_response(serializer.data, author_id, post_id)

        serializer = CommentSerializer(
            comments, many=True, context={'request': request})
        return Response(serializer.data)

    def get_custom_paginated_response(self, data, author_id, post_id):
        # Constructing the custom response format
        page_num = self.request.query_params.get(
            self.pagination_class.page_query_param, 1)
        page_size = self.request.query_params.get(
            self.pagination_class.page_size_query_param, self.pagination_class.page_size)
        return Response({
            "type": "comments",
            "page": int(page_num),
            "size": int(page_size),
            "post": f"{make_post_url(HOST_URL, author_id, post_id)}",
            "id": f"{make_comments_url(HOST_URL, author_id, post_id)}",
            "comments": data,
        })

    @swagger_auto_schema(
        operation_description="Create a comment on a post.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['type', 'content'],
            properties={
                "type": openapi.Schema(type=openapi.TYPE_STRING, example="comment"),
                "content": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'post_id',
                in_=openapi.IN_PATH,
                description='ID of a post',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={201: CommentSerializer()},
    )

    def post(self, request, author_id, post_id):
        post = get_object_or_404(Post, id=post_id, author__uid=author_id)
        # Check if the request user can access the post to comment
        if not self.can_view_comments(post, request.user):
            return Response({"detail": "You do not have permission to comment on this post."}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if 'type' is present in the request and is exactly 'comment'
        if request.data.get('type') != 'comment':
            return Response({"detail": "Invalid type. This field must be 'comment'."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CommentCreateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostLikesAPIView(APIView):
    """
    Retrieve all likes from other authors for a specific post of the given author.
    """
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve likes for a specific post.",
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'post_id',
                in_=openapi.IN_PATH,
                description='ID of a post',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={200: LikeSerializer(many=True)},
    )

    def get(self, request, author_id, post_id):
        # Ensure the post belongs to the specified author
        post = get_object_or_404(Post, id=post_id, author__uid=author_id)
        # Filter likes where the like's author is not the post's author
        likes = Like.objects.filter(post=post).exclude(author=post.author)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

class CommentLikesAPIView(APIView):
    """
    Retrieve all likes from other authors for a specific comment on the given author's post.
    """
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_description="Retrieve likes for a specific comment.",
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'post_id',
                in_=openapi.IN_PATH,
                description='ID of a post',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'comment_id',
                in_=openapi.IN_PATH,
                description='ID of a comment',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={200: LikeSerializer(many=True)},
    )

    def get(self, request, author_id, post_id, comment_id):
        # Ensure the comment belongs to a post of the specified author
        print("In CommentLikesAPIView")
        comment = get_object_or_404(Comment, id=comment_id)
        print("Got comment")
        # Filter likes where the like's author is not the comment's author
        likes = Like.objects.filter(comment=comment).exclude(author=comment.author)
        print("Got likes")
        serializer = LikeSerializer(likes, many=True)
        print("Serialized likes")
        return Response(serializer.data)


class AuthorLikedAPIView(APIView):
    """
    List what things a specific author has liked
    """
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Retrieve items liked by a specific author.",
        manual_parameters=[
            openapi.Parameter(
                'author_id',
                in_=openapi.IN_PATH,
                description='ID of an author stored on this server',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={200: LikeSerializer(many=True)},
    )

    def get(self, request, author_id):
        author = get_object_or_404(Author, uid=author_id)
        likes = Like.objects.filter(author=author)
        serializer = LikeSerializer(likes, many=True)
        
        # Wrap the serialized data in the specified format
        response_data = {
            "type": "liked",
            "items": serializer.data
        }
        
        return Response(response_data)

@method_decorator(csrf_exempt, name='dispatch')
class SharePostWithFriends(APIView):
    authentication_classes = [TokenAuthentication, NodesAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, author_id, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.visibility != 'PUBLIC':
            return Response({"detail": "This post can not be shared with friends."}, status=status.HTTP_400_BAD_REQUEST)
        
        send_response = send_post_to_friends(request, author_id, post_id)
        
        if send_response.status_code != 200:
            return Response({"detail": "Failed to share post with friends."}, status=send_response.status_code)
        return Response({"detail": "Post shared with friends."}, status=status.HTTP_200_OK)