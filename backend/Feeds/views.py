from django.shortcuts import get_object_or_404, render
# Ensure your import paths are correct based on your project structure
from Posts.models import Post
from Posts.serializers import PostSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User  
from .models import Author
from Posts.utils import is_friend
import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Retrieve posts for the stream view.",
    responses={200: openapi.Response("List of posts", PostSerializer)},
)

def stream_view(request):
    """
    Retrieve posts for the stream view.

    :param request: HTTP request object.
    :return: Response object.
    """
    logger = logging.getLogger(__name__)
    request_user = request.user

    logger.debug(f"User authenticated: {request_user.is_authenticated}")
    if not request_user.is_authenticated:
        # If the user is not authenticated, return only public posts
        posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
    else:
        # For authenticated users, find their corresponding Author object
        request_author = request_user
        logger.debug(f"Request author: {request_author}")
        logger.debug(f"Request user UID: {request_user.uid}")

        if request_author:
            # Fetch posts from all authors
            all_posts = Post.objects.all().order_by('-published')
            visible_posts = []

            for post in all_posts:
                # Check if the post author is the same as the request author
                if post.author == request_author:
                    if post.visibility != 'UNLISTED':
                        visible_posts.append(post)
                else:
                    # Check if the request author is friends with the post's author
                    if is_friend(request_author, post.author):
                        # Friends can see public, friends-only, and unlisted posts except those explicitly unlisted
                        if post.visibility != 'UNLISTED':
                            visible_posts.append(post)
                    elif post.visibility == 'PUBLIC':
                        # Default case for non-friends: only public posts
                        visible_posts.append(post)

            posts = visible_posts
            logger.debug(f"Visible posts: {visible_posts}")

    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)
