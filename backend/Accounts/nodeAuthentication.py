from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Author
from django.contrib.auth.hashers import check_password


class NodesAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        try:
            print('In node authentication')
            node = Author.objects.get(username=userid, is_a_node=True)
            
        except Author.DoesNotExist:
            raise AuthenticationFailed('No such node')
        if password != node.password:
            
            raise AuthenticationFailed('Incorrect password')
        
        print(node)
        return (node, None)

