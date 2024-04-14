from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    # URL pattern for listing all posts by an author or creating a new post
    path('authors/<uuid:author_id>/posts/',
         views.AuthorPosts.as_view(), name='author-posts'),
    path('authors/<uuid:author_id>/posts',
         views.AuthorPosts.as_view(), name='author-posts-notrailing'),

    # URL pattern for retrieving, updating, or deleting a specific post by an author
    path('authors/<uuid:author_id>/posts/<uuid:post_id>',
         views.AuthorPost.as_view(), name='author-post-notrailing'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/',
         views.AuthorPost.as_view(), name='author-post'),

    # URL pattern for serving the image of a specific post by an author
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/image',
         views.ServeImagePost.as_view(), name='serve-image-post-notrailing'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/image/',
         views.ServeImagePost.as_view(), name='serve-image-post'),

    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments',
         views.PostComments.as_view(), name='comments-post-notrailing'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/comments/',
         views.PostComments.as_view(), name='comments-post'),

    # URL for retrieving likes on a specific post by an author
    path('authors/<str:author_id>/posts/<str:post_id>/likes',
         views.PostLikesAPIView.as_view(), name='post_likes-notrailing'),
    path('authors/<str:author_id>/posts/<str:post_id>/likes/',
         views.PostLikesAPIView.as_view(), name='post_likes'),

    # URL for retrieving likes on a specific comment by an author
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes',
         views.CommentLikesAPIView.as_view(), name='comment_likes-notrailing'),
    path('authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes/',
         views.CommentLikesAPIView.as_view(), name='comment_likes'),

    # URL for listing all likes made by an author
    path('authors/<str:author_id>/liked',
         views.AuthorLikedAPIView.as_view(), name='author_likes-notrailing'),
    path('authors/<str:author_id>/liked/',
         views.AuthorLikedAPIView.as_view(), name='author_likes'),

    path('authors/<uuid:author_id>/posts/<uuid:post_id>/image',
         views.ServeImagePost.as_view(), name='serve-image-post-notrailing'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/image/',
         views.ServeImagePost.as_view(), name='serve-image-post'),

    # URL pattern for retrieving, updating, or deleting an unlisted post by an author
    path('authors/<uuid:author_id>/posts/<str:unlisted_uri>/',
         views.AuthorPost.as_view(), name='author-post-unlisted'),
    path('authors/<uuid:author_id>/posts/<str:unlisted_uri>',
         views.AuthorPost.as_view(), name='author-post-unlisted-notrailing'),

    path('authors/<uuid:author_id>/posts/<uuid:post_id>/sharewithfriends/',
         views.SharePostWithFriends.as_view(), name='share_with_friends'),
    path('authors/<uuid:author_id>/posts/<uuid:post_id>/sharewithfriends',
         views.SharePostWithFriends.as_view(), name='share_with_friends-notrailing'),
]
