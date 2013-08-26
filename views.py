from django.http import HttpResponse #Http404, HttpResponseRedirect, 
from django.shortcuts import render #get_object_or_404, 
#from django.core.urlresolvers import reverse
from django.utils import timezone
from django.template import RequestContext, loader
from dateutil import parser
from GoProApp.models import *
import json

# Create your views here.

def control(request):
    camera_set = Camera.objects.all().order_by('name')
    
    for camera in camera_set:
        camera.status = json.loads(camera.status)
        
    context = {
        'active_nav': 'control',
        'camera_set': camera_set
    }
    return render(request, 'GoProApp/control.html', context)

def preview(request):
    context = {
        'active_nav': 'preview',
    }
    return render(request, 'GoProApp/preview.html', context)

def api(request, action = None):
    response = {}
    
    if action == 'updateCameras':
        response['time'] = str( timezone.now() )
        
        # parse input parameters
        lastUpdate = None
        if 'last_update' in request.GET:
            lastUpdate = parser.parse(request.GET['last_update'])
        
        # build list
        camera_set = Camera.objects.all().order_by('name')
        response['list'] = []
        template = loader.get_template('GoProApp/control_camera_row.html')
        for camera in camera_set:
            data = {}
            data['id'] = camera.id
            
            # only need to send bulk of data if the client hasn't seen this object before
            if not lastUpdate or (camera.last_attempt is not None and camera.last_attempt >= lastUpdate) or camera.date_added >= lastUpdate:
                camera.status = json.loads(camera.status)
                data['html'] = template.render(RequestContext(request, {
                    'camera': camera,
                }))
            
            response['list'].append(data)
    
    elif action == 'updateCommands':
        response['time'] = str( timezone.now() )
        
        # parse input parameters
        lastUpdate = None
        if 'last_update' in request.GET:
            lastUpdate = parser.parse(request.GET['last_update'])
        
        # build list
        command_set = CameraCommand.objects.filter(time_completed__isnull=True).order_by('time_requested')
        response['list'] = []
        template = loader.get_template('GoProApp/control_command_row.html')
        for command in command_set:
            data = {}
            data['id'] = command.id
            
            # only need to send bulk of data if the client hasn't seen this object before
            if not lastUpdate or command.date_added >= lastUpdate:
                data['html'] = template.render(RequestContext(request, {
                    'command': command,
                }))
            
            response['list'].append(data)
    
    elif action == 'sendCommands':
        commands = json.loads(request.GET['commands'])
        request_time = timezone.now()
        
        for command in commands:
            try:
                camera = Camera.objects.get(pk=int(command[0]))
                c = CameraCommand(camera=camera, command=command[1], time_requested=request_time)
                c.save()
            except:
                pass
    
    elif action == 'deleteCommand':
        command = CameraCommand.objects.get(pk=int(request.GET['command']))
        command.delete()
    
    # prep response for output
    if 'callback' in request.GET:
        response = request.GET['callback'] + '(' + json.dumps(response) + ')'
    else:
        response = json.dumps(response)
    
    # send response
    return HttpResponse(response, content_type="application/json")