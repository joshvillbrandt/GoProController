from django.http import HttpResponse #Http404, HttpResponseRedirect, 
from django.shortcuts import render #get_object_or_404, 
#from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from django.template import RequestContext, loader
from dateutil import parser
from GoProApp.models import *
import json

# Create your views here.

def control(request):
    context = {
        'active_nav': 'control'
    }
    return render(request, 'GoProApp/control.html', context)

def raw(request):
    context = {
        'active_nav': 'raw'
    }
    return render(request, 'GoProApp/raw.html', context)

def preview(request):
    context = {
        'active_nav': 'preview',
    }
    return render(request, 'GoProApp/preview.html', context)

def api(request, action = None):
    response = {}
    
    if action == 'updateCameras':
        response['time'] = str( timezone.now() )
        response['extra'] = {}
        
        # parse input parameters
        lastUpdate = None
        if 'last_update' in request.GET:
            lastUpdate = parser.parse(request.GET['last_update'])
        
        # build list
        camera_set = Camera.objects.all().order_by('name')
        response['list'] = []
        if "preview" in request.GET:
            template = loader.get_template('GoProApp/preview_row.html')
        else:
            template = loader.get_template('GoProApp/control_camera_row.html')
        for camera in camera_set:
            data = {}
            data['id'] = camera.id
            
            # send entire json if requested
            if 'status' in request.GET:
                data['status'] = camera.status
            
            # only need to send bulk of data if the client hasn't seen this object before
            camera.status = json.loads(camera.status)
            if not lastUpdate or (camera.last_attempt is not None and camera.last_attempt >= lastUpdate) or camera.date_added >= lastUpdate:
                data['html'] = template.render(RequestContext(request, {
                    'camera': camera,
                }))
                data['image'] = camera.image
                
            # calculate last update
            data['extra'] = {}
            if camera.last_update == None:
                data['extra']['.last-update'] = "never"
            else:
                diff = timezone.now() - camera.last_update
                minutes = divmod(diff.days * 86400 + diff.seconds, 60)[0]
                if minutes > 60:
                    data['extra']['.last-update'] = ">1 hour"
                else:
                    data['extra']['.last-update'] = str(minutes) + " minutes"
            
            # push this camera to the reponse
            response['list'].append(data)
        
        # determine proxy health
        camera_set = Camera.objects.filter(last_attempt__gte=timezone.now()-timedelta(seconds=30))
        if len(camera_set) > 0:
            response['extra']['.proxy-health'] = "<span class=\"label label-default\">proxy is alive</span>"
        else:
            response['extra']['.proxy-health'] = "<span class=\"label label-danger\">proxy is dead</span>"
    
    elif action == 'updateCommands':
        response['time'] = str( timezone.now() )
        
        # parse input parameters
        lastUpdate = None
        if 'last_update' in request.GET:
            lastUpdate = parser.parse(request.GET['last_update'])
        
        # build list
        command_set = CameraCommand.objects.filter(time_completed__isnull=True).order_by('date_added')
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
        
        # determine cmd delay
        response['extra'] = {}
        command_set = CameraCommand.objects.filter(time_completed__isnull=False).order_by('-time_completed')[:10]
        sum = 0
        avg = 0
        for command in command_set:
            sum += (command.time_completed-command.date_added).total_seconds()
        if len(command_set) > 0:
            avg = sum / len(command_set)
        response['extra']['.cmd-time'] = round(avg, 2)
    
    elif action == 'sendCommands':
        commands = json.loads(request.GET['commands'])
        
        for command in commands:
            try:
                camera = Camera.objects.get(pk=int(command[0]))
                c = CameraCommand(camera=camera, command=command[1])
                c.save()
            except:
                pass
    
    elif action == 'editCamera':
        pk = request.GET['pk']
        
        if pk == 'new':
            c = Camera(name=request.GET['name'], ssid=request.GET['ssid'], password=request.GET['password'])
            c.save()
        else:
            c = Camera.objects.get(pk=pk)
            c.name = request.GET['name']
            c.ssid = request.GET['ssid']
            c.password = request.GET['password']
            c.save()
    
    elif action == 'deleteCommand':
        command = CameraCommand.objects.get(pk=int(request.GET['pk']))
        command.delete()
    
    elif action == 'deleteCamera':
        command = Camera.objects.get(pk=int(request.GET['pk']))
        command.delete()
    
    # prep response for output
    if 'callback' in request.GET:
        response = request.GET['callback'] + '(' + json.dumps(response) + ')'
    else:
        response = json.dumps(response)
    
    # send response
    return HttpResponse(response, content_type="application/json")
