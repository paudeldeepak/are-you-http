from django.shortcuts import render

# Create your views here.

from django.http import HttpRequest,HttpResponse
from .models import ConnectedServer
from .serializers import ConnectedServerSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json

#gets all connected servers so we can list them in the user search screen
@swagger_auto_schema(
    operation_description="Get all connected servers.",
    responses={200: openapi.Response("List of connected servers", schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'servers': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))}))},
)
def get_all_connected_servers(request):
    """
    Get all connected servers.

    :param request: HTTP request object.
    :return: Response object.
    """
    connected = ConnectedServer.objects.all()
    serialized = [ConnectedServerSerializer(x).data for x in connected]
    resp = {"servers" : serialized}
    return HttpResponse(content=json.dumps(resp),status=200)