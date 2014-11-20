from django.contrib import admin
from GoProController.models import *

# Register your models here

# For more information on this file, see
# https://docs.djangoproject.com/en/dev/intro/tutorial02/


class CameraCommandInline(admin.StackedInline):
    model = CameraCommand
    fields = ['command', 'time_completed']
    extra = 0
admin.site.register(CameraCommand)


class CameraAdmin(admin.ModelAdmin):
    fields = ['name', 'ssid', 'password', 'status', 'last_update', 'image']
    inlines = [CameraCommandInline]
admin.site.register(Camera, CameraAdmin)
