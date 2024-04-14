from django.db import models
from Accounts.models import Author
from django.utils.timezone import now
import uuid

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_url = models.URLField(default='', blank=True, null=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.URLField(default='', blank=True, null=True)
    origin = models.URLField(default='', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contentType = models.CharField(max_length=50, choices=[(
        'text/markdown', 'Markdown'), ('text/plain', 'Plain Text'), ('image/png;base64', 'PNG Image'), ('image/jpeg;base64', 'JPEG Image')])
    published = models.DateTimeField(default=now)
    visibility = models.CharField(max_length=10, choices=[(
        'PUBLIC', 'Public'), ('FRIENDS', 'Friends'), ('UNLISTED', 'Unlisted')])
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
   
   
    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    id_url = models.URLField(default='', blank=True, null=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    contentType = models.CharField(max_length=50, choices=[(
        'text/markdown', 'Markdown'), ('text/plain', 'Plain Text')])
    published = models.DateTimeField(default=now)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='likes',  null=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='likes', null=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='likes')
    published = models.DateTimeField(default=now)

    class Meta:
        unique_together = [['post', 'author'], ['comment', 'author']]

    def __str__(self):
        if self.post:
            return f'Like by {self.author.username} on post "{self.post.title}"'
        elif self.comment:
            return f'Like by {self.author.username} on comment "{self.comment.comment}"'
