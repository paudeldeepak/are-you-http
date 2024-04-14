from django.contrib import admin
from .models import Author, Friendship,Inbox_Feed
#my Post app has its model file containing post, like, comment need to import them here
from Posts.models import Post, Like, Comment
from rest_framework.authtoken.admin import TokenAdmin

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('uid','username', 'is_approved', 'is_remote')
    list_filter = ('is_approved',)
    actions = ['approve_authors', 'disapprove_authors']
    readonly_fields = ('id',)  # Updated from 'uid' to 'id'

    def approve_authors(self, request, queryset):
        queryset.update(is_approved=True)

    def disapprove_authors(self, request, queryset):
        queryset.update(is_approved=False)
        
    
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('uid','actor', 'object', 'status', 'summary')
    
    

@admin.register(Inbox_Feed)
class Inbox_FeedAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'sender', 'post', 'comment', 'like', 'friendship', 'published')
    list_filter = ('published',)
    

TokenAdmin.raw_id_fields = ['user']