
from Accounts.models import Friendship, Author, Inbox_Feed
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from Posts.models import Post
from Social.models import ConnectedServer
from Posts.serializers import PostSerializer
from django.http import JsonResponse
import requests
import json


def send_post_to_friends(request, author_id, post_id):
    author = get_object_or_404(Author, uid=author_id)
    post = get_object_or_404(Post, id=post_id)

    # Check if the post visibility is set to 'Friends' or public
    if post.visibility == 'UNLISTED':
        return JsonResponse({"detail": "The post is not set to a visibility that is shareable"}, status=400)

    # Fetch all friends of the author
    friends_relationships = Friendship.objects.filter(
        Q(object=author, status=3) | Q(actor=author, status=3)
    ).distinct()

    # Use a set to collect unique friend IDs
    friend_ids = {fr.actor_id if fr.object_id ==
                  author_id else fr.object_id for fr in friends_relationships}

    # Fetch all friend Author instances based on the unique IDs
    friends = Author.objects.filter(uid__in=friend_ids)

    # Assuming a function or method exists to send the post
    for friend in friends:
        # Implement according to your application's logic
        send_post_to_inbox(request, post, friend)

    return JsonResponse({"detail": "Post sent to friends' inboxes."}, status=200)


def send_post_to_inbox(request, post, author):
    """
    Send a post to an author's inbox.
    Args:
        request: HttpRequest object.
        post: Post instance to send.
        author: Author instance to send the post to.
    Returns:
        JsonResponse: Status of the operation.
    """
    # check if author is local or remote
    if author.is_remote:
        node = get_object_or_404(ConnectedServer, host=author.host)
        url = node.api + 'authors/' + str(author.uid) + '/inbox/'
        serializer = PostSerializer(post, context={'request': request})
        response = requests.post(url, data=json.dumps(
            serializer.data), auth=(node.username, node.password),
            headers={'Content-Type': 'application/json'})
        return response
    else:
        inbox_feed = Inbox_Feed.objects.create(
            sender=post.author,
            receiver=author, post=post)
        inbox_feed.save()
        return JsonResponse({"detail": "Post sent to inbox."}, status=status.HTTP_200_OK)

def send_post_to_following(request, author_id, post_id):
    author = get_object_or_404(Author, uid=author_id)
    post = get_object_or_404(Post, id=post_id)

    # get all the objects that are following the author
    following = Friendship.objects.filter(
        Q(object=author) & Q(status__in=[2, 3])
    ).distinct()

    # use a set to collect the people that are following id
    following_ids = {f.actor.uid for f in following}
    
    # fetch all the authors that are following the author
    following_authors = Author.objects.filter(uid__in=following_ids)
    
    # send the post to the following authors
    for following_author in following_authors:
        send_post_to_inbox(request, post, following_author)
        
    return JsonResponse({"detail": "Post sent to following authors."}, status=200)