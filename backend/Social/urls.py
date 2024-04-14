from django.urls import path
from . import views
from .views import get_all_connected_servers

urlpatterns = [
    path("connected-servers/",get_all_connected_servers),
]