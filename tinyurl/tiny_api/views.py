from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from tiny_api.managers import TinyUrlManager


@api_view(['GET'])
def get_full_url(request, short_url):
    manager = TinyUrlManager("tinyurl")
    result = manager.get_full_url(short_url)
    if result:
        return HttpResponseRedirect(redirect_to=result)
    raise NotFound()


@api_view(['POST'])
def set_short_url(request):
    full_url = request.data.get("full_url")
    if not full_url:
        raise ValidationError("full_url is required")
    manager = TinyUrlManager("tinyurl")
    result = manager.set_short_url(full_url)
    if result:
        return Response({
            "short_url": result,
            "full_url": full_url,
        }, status=status.HTTP_201_CREATED)
    raise ValidationError("Something went wrong")
