from Accounts.utils import make_author_url

def make_inbox_url(request_host: str, author_id: str) -> str:
    """Generates a URL for an author's inbox."""
    # Simplifies by reusing make_author_url
    return f"{make_author_url(request_host, author_id)}/inbox"