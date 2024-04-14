# from django.db import models
# from Accounts.models import Author
# # Create your models here.
# class Follow(models.Model):
#     follower = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='following')
#     followee = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('follower', 'followee')

#     def __str__(self):
#         return f'{self.follower.username} follows {self.followee.username}'

# class FollowRequest(models.Model):
#     sender = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='sent_follow_requests')
#     receiver = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='received_follow_requests')
#     status = models.CharField(max_length=10, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')])
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Follow request from {self.sender.username} to {self.receiver.username}'


from django.db import models
from Accounts.models import Author

class ConnectedServer(models.Model):
    host = models.TextField()
    api = models.TextField()
    username = models.TextField()
    password = models.TextField()
    is_active = models.BooleanField(default=False)