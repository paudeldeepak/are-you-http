from django.db import models
from Accounts.models import Author
from Posts.models import Comment, Like, Post
# from Social.models import FollowRequest

# # Create your models here.
# class Inbox(models.Model):
#     owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='inbox')
#     posts = models.ForeignKey(Post,on_delete=models.CASCADE, blank=True)
#     # follow_request_received = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, null=True)
#     comment = models.ForeignKey(Comment,on_delete=models.CASCADE,null=True)
#     like = models.ForeignKey(Like,on_delete=models.CASCADE,null=True)

#     def __str__(self):
#         return f'Inbox for {self.owner.username}'
