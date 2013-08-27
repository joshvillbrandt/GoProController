from django.conf.urls import patterns, url
from GoProApp import views

urlpatterns = patterns('',
    url(r'^$', views.control, name='control'),
    url(r'^raw/$', views.raw, name='raw'),
    url(r'^preview/$', views.preview, name='preview'),
    url(r'^api/(.*)/$', views.api, name='api'),
)