from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


app_name = 'Accounts'

urlpatterns = [
    path('signup', views.Signup.as_view(), name='signup-notrailing'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('signin', views.Signin.as_view(), name='signin-notrailing'),
    path('signin/', views.Signin.as_view(), name='signin'),
    path('authors/<uuid:author_id>', views.getOneAuthor,
         name='getoneauthor-notrailing'),
    path('authors/<uuid:author_id>/', views.getOneAuthor, name='getoneauthor'),
    path('authors', views.DisplayAllAuthors.as_view(),
         name='displayallauthors-notrailing'),
    path('authors/', views.DisplayAllAuthors.as_view(), name='displayallauthors'),
    path('authorsown', views.DisplayAllAuthorsOwn.as_view(),
         name='displayallauthorsown-notrailing'),
    path('authorsown/', views.DisplayAllAuthorsOwn.as_view(),
         name='displayallauthorsown'),
    path('authors/<uuid:author_id>/friends', views.FriendsListView.as_view(),
         name='displayallfriends-notrailing'),  # used
    path('authors/<uuid:author_id>/friends/',
         views.FriendsListView.as_view(), name='displayallfriends'),  # used
    path('authors/<uuid:author_id>/followers',
         views.getFollowers, name='getfollowers'),  # used
    path('authors/<uuid:author_id>/followers/',
         views.getFollowers, name='getfollowers'),  # used
    path('authors/<uuid:author_id>/followers/<uuid:foreign_author_id>',
         views.FriendshipView.as_view(), name='singlefriendship'),  # used: put, delete
    path('authors/<uuid:author_id>/followers/<uuid:foreign_author_id>/',
         views.FriendshipView.as_view(), name='singlefriendship'),  # used: put, delete
    path('authors/<uuid:author_id>/requests', views.FollowRequestView.as_view(),
         name='getfollowrequests-notrailing'),  # used: get
    path('authors/<uuid:author_id>/requests/',
         views.FollowRequestView.as_view(), name='getfollowrequests'),  # used: get
    path('authors/<uuid:author_id>/requests/pending',
         views.PendingView.as_view(), name='getpendingrequests'),  # used
    path('authors/<uuid:author_id>/requests/pending/',
         views.PendingView.as_view(), name='getpendingrequests'),  # used
    # path('authors/<uuid:author_id>/requests/<uuid:foreign_author_id>/', views.FollowRequestView.as_view(), name='send_follow_request'), # used: delete
    path('authors/<uuid:author_id>/following',
         views.FollowingView.as_view(), name='getfollowing'),  # used
    path('authors/<uuid:author_id>/following/',
         views.FollowingView.as_view(), name='getfollowing'),  # used
    path('authors/<uuid:author_id>/inbox',
         views.InboxView.as_view(), name='getinbox'),
    path('authors/<uuid:author_id>/inbox/',
         views.InboxView.as_view(), name='getinbox'),
    path('setupnode', views.SetupNode.as_view(), name='setupnode-notrailing'),
    path('setupnode/', views.SetupNode.as_view(), name='setupnode'),
    path('nodes', views.GetNodesView.as_view(), name='getnodes-notrailing'),
    path('nodes/', views.GetNodesView.as_view(), name='getnodes'),
    path('token-exchange/<str:remote_host>',
         views.TokenExchangeView.as_view(), name='token-exchange'),
    path('token-exchange/<str:remote_host>/',
         views.TokenExchangeView.as_view(), name='token-exchange'),
    # path('authors/<uuid:uid>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('checkForigenFollowing/', views.CheckFriendship.as_view(), name='checkForignFollowing-notrailing'),
    path('changeFollowStatus/', views.UpdateFriendshipFollowing.as_view(), name='changeFollowStatus-notrailing'),
]
