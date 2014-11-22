from django.conf.urls import url, include
from GoProController.models import Camera, Command
from rest_framework import serializers, viewsets, routers


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


class CommandViewSet(viewsets.ModelViewSet):
    queryset = Command.objects.all()
    serializer_class = CommandSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'cameras', CameraViewSet)
router.register(r'commands', CommandViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
]
