def make_author_url(request_host: str, author_id: str) -> str:
    """Generates a URL for an author."""
    return f"{request_host}authors/{author_id}"