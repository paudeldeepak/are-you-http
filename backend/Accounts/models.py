from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin, Group, Permission, BaseUserManager
from django.conf import settings
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework.authtoken.models import Token
from django.utils.timezone import now



class UserManager(BaseUserManager):
    def create_user(self, username, password=None, displayName=None, github=None, uid=None, **otherfields):
        if not username:
            raise ValueError("Users must have a username")
        if not password:
            raise ValueError("Users must have a password")

        # Use the provided UID if available, otherwise generate a new UUID
        uid = uid or uuid.uuid4()

        user = self.model(uid=uid, username=username, displayName=displayName, github=github, **otherfields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, username, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_approved', True)
        other_fields.setdefault('is_a_node', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, **other_fields)

        
class Author(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    uid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    displayName = models.CharField(max_length=50, null=True, blank=True)
    github = models.URLField(max_length=255, null=True, blank=True)
    host = models.CharField(max_length=255, null=True, blank=True)
    id = models.URLField(max_length=255, null = True, blank = True)
    url = models.URLField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_remote = models.BooleanField(default=False)
    #NODE FILED
    is_a_node = models.BooleanField(default=False)
    profilePicture = models.URLField(max_length=255, null=True, blank=True)
    profilePictureImage = models.ImageField(upload_to='profilepictures/', default='default-profile-picture.jpg')
    auth_token_key = models.CharField(max_length=40, blank=True, null=True)  



    # Override the groups and user_permissions fields
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name="author_groups",  
        related_query_name="author",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name="author_permissions",  
        related_query_name="author",
    )

    USERNAME_FIELD = 'username'

    @property
    def type(self):
        return 'author'

    def save(self, *args, **kwargs):
        if self.host is None:
            self.host = settings.HOST_URL
        if self.id is None:
            self.id = f'{self.host}authors/{self.uid}'
        if self.url is None:
            self.url = f'{self.host}authors/{self.uid}'
        super(Author, self).save(*args, **kwargs)
        if not self.auth_token_key:
            token, _ = Token.objects.get_or_create(user=self)
            self.auth_token_key = token.key
            super(Author, self).save(update_fields=['auth_token_key'])
        
    objects = UserManager()

class Friendship(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    actor = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='actor')
    object = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='object')
    friend_code = [(1, 'Pending'), (2, 'Following'), (3, 'Friends')]
    status = models.SmallIntegerField(choices=friend_code, default=1)
    summary = models.CharField(max_length=255, null=True, blank=True)
    @property
    def type(self):
        return 'Follow'
    
class Inbox_Feed(models.Model):
    receiver = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='reciever')
    sender = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='sender')
    post = models.ForeignKey('Posts.Post', on_delete=models.CASCADE, related_name='post',null=True, blank=True)
    comment = models.ForeignKey('Posts.Comment', on_delete=models.CASCADE, related_name='inbox_feeds',null=True, blank=True)
    like = models.ForeignKey('Posts.Like', on_delete=models.CASCADE, related_name='inbox_feeds',null=True, blank=True)
    friendship = models.ForeignKey('Friendship', on_delete=models.CASCADE, related_name='inbox_friendships', null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)
    published = models.DateTimeField(default=now)
    
class TokenMapping(models.Model):
    local_token = models.CharField(max_length=255)
    remote_token = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)