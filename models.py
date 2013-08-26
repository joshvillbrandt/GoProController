from django.db import models
from datetime import datetime
import json

# Create your models here.

class Camera(models.Model):
    statusTemplate = {
        "summary": "notfound", # one of "notfound", "off", "on", or "recording"
        "power": "?",
        "batt": "?",
        "mode": "?",
        "record": "?",
        "res": "?",
        "fps": "?",
        "fov": "?"
    }
    name = models.CharField(max_length=255)
    ssid = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    last_attempt = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    image = models.TextField(blank=True)
    status = models.TextField(blank=True) # status template above is defined by GoProController.py
    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = json.dumps(self.statusTemplate)
            self.last_attempt = datetime(2002, 6, 1)
            super(Camera, self).save(*args, **kwargs)
        else:
            super(Camera, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.name

class CameraCommand(models.Model):
    COMMANDS = (
        ('power_off', 'Power Off'),
        ('power_on', 'Power On'),
        ('record_off', 'Record Off'),
        ('record_on', 'Record On'),
        ('mode_video', 'Mode Video'),
    )
    camera = models.ForeignKey(Camera)
    command = models.CharField(max_length=255, choices=COMMANDS) # command list above is defined by GoProController.py
    date_added = models.DateTimeField(auto_now_add=True) # still need this otherwise something could get added and a client not see it (because time elapses between time_request and when the model is actually added to the db)
    time_requested = models.DateTimeField() # this isn't automatic to that we can force groups of commands have the same request time; this allows for optimization when hopping wifi networks which is expensive
    time_completed = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return self.camera.__unicode__() + ' > ' + self.command
