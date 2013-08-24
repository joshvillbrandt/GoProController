from django.db import models

# Create your models here.

class Camera(models.Model):
    name = models.CharField(max_length=255)
    ssid = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    last_attempt = models.DateTimeField('time of last status attempt')
    last_update = models.DateTimeField('time of last successful status')
    image = models.TextField(blank=True)
    status = models.TextField(blank=True)
    def __unicode__(self):
        return self.name

# class Choice(models.Model):
#     poll = models.ForeignKey(Poll)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     def __unicode__(self):
#         return self.poll.__unicode__() + ' > ' + self.choice_text
