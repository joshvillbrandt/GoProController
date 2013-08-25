from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
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

def detail(preview):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404
    context = {
        'active_nav': 'GoProApp',
        'poll': poll
    }
    return render(request, 'GoProApp/detail.html', context)

def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    context = {
        'active_nav': 'GoProApp',
        'poll': poll
    }
    return render(request, 'GoProApp/results.html', context)

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'GoProApp/detail.html', {
            'active_nav': 'GoProApp',
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
        return detail(request, poll_id)
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('GoProApp:results', args=(p.id,)))