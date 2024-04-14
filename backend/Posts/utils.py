from Accounts.models import Friendship
from Accounts.utils import make_author_url


def is_friend(author1, author2):
    """
    Check if author1 and author2 have a mutual friendship relationship.
    args:
        author1: Author instance
        author2: Author instance
    returns:
        bool: True if author1 and author2 are friends, False otherwise
    """
    # Direct friendship from author1 to author2
    direct_friendship = Friendship.objects.filter(
        actor=author1, object=author2, status=3).exists()

    # Direct friendship from author2 to author1
    reverse_friendship = Friendship.objects.filter(
        actor=author2, object=author1, status=3).exists()

    # Considered friends if both direct and reverse friendships exist
    return direct_friendship and reverse_friendship


def make_post_url(request_host: str, author_id: str, post_id: str) -> str:
    """Generates a URL for a post."""
    # Reuses make_author_url to build the initial part of the URL
    author_url = make_author_url(request_host, author_id)
    return f"{author_url}/posts/{post_id}"


def make_comments_url(request_host: str, author_id: str, post_id: str) -> str:
    """Generates a URL for the comments on a post."""
    # Directly builds on top of make_post_url for brevity
    return f"{make_post_url(request_host, author_id, post_id)}/comments"


def make_comment_url(request_host: str, comment_id: str) -> str:
    """Generates a URL for a specific comment."""
    # Builds upon make_comments_url, appending the comment ID
    return f"{request_host}/comments/{comment_id}"

