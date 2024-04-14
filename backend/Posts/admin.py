from django.contrib import admin
from .models import Post, Comment, Like
from django import forms

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'author', 'published', 'visibility', 'content_type_display')
    list_filter = ('published', 'visibility', 'contentType')
    search_fields = ('title', 'content', 'author__username')  # Adjust according to your Author model
    ordering = ('-published',)

    def content_type_display(self, obj):
        """Display the readable value for the contentType field.
        """
        return obj.get_contentType_display()
    content_type_display.short_description = 'Content Type'
    
admin.site.register(Post, PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'published')
    list_filter = ('published',)
    search_fields = ('comment', 'author__username')  # Adjust according to your Author model
    ordering = ('-published',)
    
admin.site.register(Comment, CommentAdmin)


class LikeAdminForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = '__all__'  

    def __init__(self, *args, **kwargs):
        super(LikeAdminForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = False  # Make the comment field not required
        self.fields['post'].required = False  # Ensure the post field is also optional in the admin

class LikeAdmin(admin.ModelAdmin):
    form = LikeAdminForm
    list_display = ('id', 'post', 'comment', 'author', 'published')
    list_filter = ('published',)
    search_fields = ('author__username',)  # Adjust according to your Author model
    ordering = ('-published',)
    
admin.site.register(Like, LikeAdmin)