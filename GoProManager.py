#!/usr/bin/python

# GoProController.py
# Josh Villbrandt <josh@javconcepts.com>
# 8/24/2013

# import django settings
import os, sys
sys.path.append('/var/sites/GoProSite/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'GoProSite.settings'
import GoProSite

# import django models
from GoProApp.models import *

# import controller
from GoProController import GoProController
controller = GoProController()

# other includes
from django.utils import timezone
import json
import time

# execute a command
def connectToCamera(ssid, password, command = None):
    print 'hey'
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

# keep running until we land on Mars (and come back?)
while "people" != "on Mars":
    doneAnything = False # just so i don't have to write a bunch of nasty embedded if statements
    
    # send a command for the network we are currently on if possible
    command_set = CameraCommand.objects.filter(camera__ssid__exact=controller.currentSSID)
    if not doneAnything and len(command_set) > 0:
        pass
    
    # send a command if the queue has something in it
    command_set = CameraCommand.objects.all().order_by('time_requested')
    
    # otherwise check status of the most stale camera
    camera = Camera.objects.all().order_by('-last_attempt')
    
    # protect the cpu in the event that there was nothing to do
    time.sleep(0.01)
    