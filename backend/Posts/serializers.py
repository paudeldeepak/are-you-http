from rest_framework import serializers
from Accounts.serializers import AuthorSerializer
from django.urls import reverse
from .models import *
from .utils import make_post_url, make_comment_url
from backend.settings import HOST_URL


class PostSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id_url')
    type = serializers.CharField(default='post', read_only=True)
    author = AuthorSerializer(read_only=True)
    count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    source = serializers.CharField(source='id_url')
    origin = serializers.CharField(source='id_url')

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType',
                'content', 'author', 'count', 'comments', 'published', 'visibility']
        read_only_fields = ['type', 'author', 'count', 'comments']

    def get_count(self, obj):
        return Comment.objects.filter(post=obj).count()

    def get_comments(self, obj):
        request = self.context.get('request')
        if request:
            comments_url = reverse(
                'posts:comments-post',
                kwargs={'author_id': str(
                    obj.author.uid), 'post_id': str(obj.id)},
            )
            # Use request.build_absolute_uri to get the full URL
            return request.build_absolute_uri(comments_url)
        return None

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr != 'author':
                setattr(instance, attr, value)
        instance.save()
        return instance


class PostCreateSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['title', 'id', 'source', 'origin', 'description', 'contentType',
                'content', 'author', 'published', 'visibility']
        read_only_fields = ['author']

    def create(self, validated_data):
        author = self.context['request'].user
        validated_data['author'] = author
        post = Post.objects.create(**validated_data)
        post_id_url = make_post_url(HOST_URL, str(author.uid), str(post.id))
        post.id_url = post_id_url
        post.save()
        return post


class CommentSerializer(serializers.ModelSerializer):
    "Comment Serializer"
    id = serializers.CharField(source='id_url')
    type = serializers.CharField(default='comment', read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        "Fields to be serialized from Comment model"
        fields = ['type', 'author',
                'comment', 'contentType', 'published', 'id']


class CommentCreateSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['author', 'comment', 'contentType', 'published', 'id']

    def create(self, validated_data):
        author = self.context['request'].user
        validated_data['author'] = author
        comment = Comment.objects.create(**validated_data)
        comment_id_url = make_comment_url(comment.post.id_url,str(comment.id))
        comment.id_url = comment_id_url
        comment.save()
        return comment

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['summary', 'type', 'author', 'object']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = {
            "type": "author",
            "id": instance.author.id,
            "host": instance.author.host,
            "displayName": instance.author.displayName,
            "url": instance.author.url,
            "github": instance.author.github,
            "profileImage": instance.author.profilePicture
        }
        
        return representation

    summary = serializers.SerializerMethodField()
    type = serializers.CharField(default='Like')
    object = serializers.SerializerMethodField()

    def get_summary(self, obj):
        if obj.post:
            return f"{obj.author.displayName} likes your post"
        else:
            return f"{obj.author.displayName} likes your comment"
    
    def get_object(self, obj):
        if obj.post:
            return obj.post.id_url
        else:
            return obj.comment.id_url
    
