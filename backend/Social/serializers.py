from rest_framework import serializers
from .models import ConnectedServer  # Import the ConnectedServer model directly from your models.py file

class ConnectedServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedServer  # Reference the ConnectedServer model correctly
        fields = ['host', 'api', 'username', 'password']
