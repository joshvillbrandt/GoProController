import json
from django.conf.urls import url, include
from GoProController.models import Camera, Command
from rest_framework import serializers, viewsets, routers, filters
from django.http import HttpResponse
from goprohero import GoProHero


# Serializers define the API representation.
class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command


# ViewSets define the view behavior.
class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filter_backends = (filters.OrderingFilter,)


class CommandViewSet(viewsets.ModelViewSet):
    queryset = Command.objects.all()
    serializer_class = CommandSerializer
    filter_backends = (filters.OrderingFilter,)


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'cameras', CameraViewSet)
router.register(r'commands', CommandViewSet)


# A view to return the GoProHero config dictionary
def ConfigView(request):
    data = GoProHero.config()
    return HttpResponse(json.dumps(data), content_type="application/json")


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^config', ConfigView)
]
