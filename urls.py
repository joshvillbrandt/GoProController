from django.conf.urls import patterns, url
from GoProApp import views

urlpatterns = patterns('',
    url(r'^$', views.control, name='control'),
    url(r'^preview/$', views.preview, name='preview'),
    url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)