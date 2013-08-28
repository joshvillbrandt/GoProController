from django.db import models
from datetime import datetime
import json

# Create your models here.

class Camera(models.Model):
    statusTemplate = {
        "summary": "notfound", # one of "notfound", "off", "on", or "recording"
        "raw": {}
    }
    name = models.CharField(max_length=255)
    ssid = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    last_attempt = models.DateTimeField(auto_now=True) 
    last_update = models.DateTimeField(null=True, blank=True)
    image = models.TextField(blank=True)
    status = models.TextField(blank=True) # status template above is defined by GoProController.py
    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = json.dumps(self.statusTemplate)
            self.last_attempt = datetime(2002, 6, 1) # what's this date?! ;)
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
        ('mode_still', 'Mode Still'),
    )
    camera = models.ForeignKey(Camera)
    command = models.CharField(max_length=255, choices=COMMANDS) # command list above is defined by GoProController.py
    date_added = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return self.camera.__unicode__() + ' > ' + self.command
