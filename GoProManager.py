#!/usr/bin/python

# GoProController.py
# Josh Villbrandt <josh@javconcepts.com>
# 8/24/2013


# # import django settings
# import os, sys
# sys.path.append('var/sites/GoProSite/')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'GoProSite.settings'
# from ..GoProSite import settings
# 
# # process django settings
# from django.core.management import setup_environ
# setup_environ(settings)
# 
# # import django models
# from GoProApp.models import Camera

# import django settings
import os, sys
sys.path.append('/var/sites/GoProSite/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'GoProSite.settings'
import GoProSite

# # import django models
from GoProApp.models import *

# import controller
from GoProController import GoProController
controller = GoProController()

# other includes
from django.utils import timezone
import json

# loop unless someone tells us to stop

# send a command if the queue has something in it

# otherwise check status of the most stale camera
camera_set = Camera.objects.all()
for camera in camera_set:
    # connect to camera Ad-Hoc network
    camera.last_attempt = timezone.now()
    print 'connecting to ' + camera.ssid + '...'
    wifiConnected = controller.connect(camera.ssid, camera.password)
    
    # preload empty camera status
    if camera.status == "":
        camera.status = json.dumps(controller.statusTemplate)
    
    if wifiConnected:
        # get current status
        status = controller.getStatus()
        
        # save results to db
        if status['summary'] != 'notfound':
            if status['power'] == 'on':
                camera.status = json.dumps(status)
                camera.last_update = camera.last_attempt
            else:
                # lets just save the fact that the camera is off
                camera.status = json.loads(camera.status)
                camera.status['summary'] = status['summary']
                camera.status['power'] = status['power']
                camera.status = json.dumps(camera.status)
    else:
        camera.status = json.loads(camera.status)
        camera.status['summary'] = 'notfound'
        camera.status = json.dumps(camera.status)
        
    
    camera.save()