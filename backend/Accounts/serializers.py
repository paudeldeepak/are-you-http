from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
# from Posts.serializers import *
from .models import *
from rest_framework.validators import UniqueValidator, ValidationError
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.urls import reverse
# from .serializers import *
from rest_framework.authtoken.models import Token
from Posts.models import *


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True, validators=[
                                     UniqueValidator(queryset=Author.objects.all())], max_length=30)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    displayName = serializers.CharField(required=True, max_length=50)
    github = serializers.URLField(
        required=False, allow_blank=True, max_length=255)

    class Meta:
        model = Author
        fields = ('username', 'password', 'password2',
                  'displayName', 'github', 'profilePictureImage')

    def create(self, validated_data):

        user_data = {
            "username": validated_data['username'],
            "password": validated_data['password'],
            "displayName": validated_data['displayName'],
            "github": validated_data['github'],
        }
        if validated_data.get('profilePictureImage') is not None:
            user_data = {
                **user_data, "profilePictureImage": validated_data['profilePictureImage']}
        user = Author.objects.create_user(**user_data)
        return user

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        username_exist = Author.objects.filter(
            username=attrs['username']).exists()
        if username_exist:
            raise serializers.ValidationError(
                {"username": "Username is already taken."})
        return super().validate(attrs)


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data['username']
        password = data['password']
        author = authenticate(request=self.context.get(
            'request'), username=username, password=password)
        if not author:
            raise serializers.ValidationError('Invalid Credentials')
        if not author.is_approved:
            raise serializers.ValidationError('Author is not approved')
        data['author'] = author
        return data


class AuthorSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(allow_null=True)
    github = serializers.URLField(allow_blank=True, allow_null=True)
    profileImage = serializers.SerializerMethodField()
    profilePictureImage = serializers.ImageField(
        write_only=True, required=False)

    class Meta:
        model = Author
        fields = ('type', 'id', 'uid', 'url', 'displayName', 'profileImage', 'profilePictureImage', 'github', 'host', 'username',
                  'is_a_node', 'is_remote', 'auth_token_key')

    def create(self, validated_data):
        author = Author.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            displayName=validated_data['displayName'],
            github=validated_data.get('github'),
            profilePictureImage=validated_data.get('profilePictureImage'),
            is_a_node=validated_data.get('is_a_node'),
            is_remote=validated_data.get('is_remote'),
        )
        author.id = f'{author.host}authors/{author.uid}'
        author.url = f'{author.host}authors/{author.uid}'
        author.save()
        return author

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.displayName = validated_data.get(
            'displayName', instance.displayName)
        instance.github = validated_data.get('github', instance.github)
        if validated_data.get('profilePictureImage') is not None:
            instance.profilePictureImage = validated_data.get(
                'profilePictureImage', instance.profilePictureImage)
        instance.save()
        return instance
    


    def get_profileImage(self, obj):
            if obj.profilePicture:
                if obj.is_remote and not obj.profilePicture.startswith('http'):
                    # Concatenate host and profilePicture if it's a remote author
                    return obj.host.rstrip('/') + obj.profilePicture
                return obj.profilePicture
            elif obj.profilePictureImage:
                # Use the domain of your service to create an absolute URL
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.profilePictureImage.url)
            return None




class FriendsSerializer(serializers.ModelSerializer):
    actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = Friendship
        fields = ('type', 'summary', 'actor', 'object')

    def create(self, validated_data):
        actor_data = validated_data.pop('actor')
        object_data = validated_data.pop('object')
        actor = Author.objects.get(uid=actor_data['id'].split('/')[-1])
        object = Author.objects.get(uid=object_data['id'].split('/')[-1])
        friendship = Friendship.objects.create(
            summary=validated_data['summary'], actor=actor, object=object, status=1)
        return friendship


# class InboxSerializer(serializers.ModelSerializer):
#     contentObject = serializers.SerializerMethodField()
#     class Meta:
#         model = Inbox_Feed
#         fields = '__all__'
#     def get_contentObject(self, object):
#         model = object.content_type.model_class()
#         #Need to add Like and Comment serializer
#         obj_contents = model.objects.get(uid = object.object_id)
#         request = self.context.get('request')
#         if isinstance(obj_contents, Friendship):
#             return FriendsSerializer(obj_contents, context={'request': request}).data
#         elif isinstance(obj_contents, Post):
#             return PostSerializer(obj_contents, context={'request': request}).data
#         else:
#             raise Exception('Unexpected type of content object - wrong model')


class FollowingSerializer(serializers.ModelSerializer):
    # actor = AuthorSerializer()
    object = AuthorSerializer()

    class Meta:
        model = Friendship
        fields = ('type', 'summary', 'object')