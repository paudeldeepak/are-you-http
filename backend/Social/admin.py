from django.contrib import admin
from .models import ConnectedServer

class ConnectedServerAdmin(admin.ModelAdmin):
    list_display = ('host','api', 'username', 'password', 'is_active')  # Display the host and username in the admin list view
    fields = ('host', 'api', 'username', 'password', 'is_active')  # Include all the fields in the admin form

# Register your models with the custom admin class
admin.site.register(ConnectedServer, ConnectedServerAdmin)
