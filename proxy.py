#!/usr/bin/python

# proxy.py
# Josh Villbrandt <josh@javconcepts.com>
# 8/24/2013

import django
import logging
import json
import time
import sys
import os
from goprohero import GoProHero
from wireless import Wireless
from django.utils import timezone
import subprocess
from colorama import Fore

# import django models
sys.path.append('/home/GoProController')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GoProController.settings")
django.setup()
from GoProController.models import Camera, Command


# asynchronous daemon to do our` bidding
class GoProProxy:
    maxRetries = 3

    # init
    def __init__(self, log_level=logging.INFO):
        # setup camera
        self.camera = GoProHero()

        # setup wireless
        interface = os.environ.get('GOPRO_WIFI_INTERFACE', None)
        self.wireless = Wireless(interface)

        # setup log
        log_file = '/var/log/gopro-proxy.log'
        log_format = '%(asctime)s   %(message)s'
        logging.basicConfig(format=log_format, level=log_level)

        # file logging
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(log_format))
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(fh)

    # connect to the camera's network
    def connect(self, camera):
        func_str = 'GoProProxy.connect({}, {})'.format(
            camera.ssid, camera.password)

        # jump to a new network only if needed
        if self.wireless.current() != camera.ssid:
            r = self.wireless.connect(
                ssid=camera.ssid, password=camera.password)

        # evaluate connection request
        if self.wireless.current() == camera.ssid:
            # reconfigure the password in the camera instance
            self.camera.password(camera.password)

            logging.info('{}{}{}'.format(Fore.CYAN, func_str, Fore.RESET))
            return True
        else:
            logging.info('{}{} - network not found{}'.format(
                Fore.YELLOW, func_str, Fore.RESET))
            return False

    # send command
    def sendCommand(self, command):
        # make sure we are connected to the right camera
        if self.connect(command.camera):
            # try to send the command, a few times if needed
            i = 0
            result = False
            while i < self.maxRetries and result is False:
                result = self.camera.command(command.command, command.value)
                i += 1
            command.time_completed = timezone.now()

            # did we successfully talk to the camera?
            self.updateCounters(command.camera, result)

            # save result
            command.save()

    # get status
    def getStatus(self, camera):
        # make sure we are connected to the right camera
        camera.last_attempt = timezone.now()
        connected = self.connect(camera)

        # could we find the camera?
        if connected:
            # update counters
            camera.last_update = camera.last_attempt
            self.updateCounters(camera, True)

            # try to get the camera's status
            status = self.camera.status()
            camera.summary = status['summary']

            # extend existing status if possible
            if camera.status != '':
                # allows us to retain knowledge of settings when powered off
                try:
                    old_status = json.loads(camera.status)
                    if old_status != '':
                        old_status.update(status)
                        status = old_status
                except ValueError:
                    logging.info('{}{} - existing status malformed{}'.format(
                        Fore.YELLOW, 'GoProProxy.getStatus()', Fore.RESET))

            # save status to camera
            camera.status = json.dumps(status)

            # grab snapshot when the camera is powered on
            if 'power' in status and status['power'] == 'on':
                image = self.camera.image()
                if image is not False:
                    camera.image = image
                    camera.image_last_update = camera.last_attempt
        else:
            # update counters
            self.updateCounters(camera, False)

            # update status
            camera.summary = 'notfound'

        # save result
        camera.save()

    def shouldBeOn(self, command):
        return command.command != 'power' or command.value != 'sleep'

    def updateCounters(self, camera, success):
        camera.connection_attempts += 1
        if success is not True:
            camera.connection_failures += 1

    # main loop
    def run(self):
        logging.info('{}GoProProxy.run(){}'.format(Fore.GREEN, Fore.RESET))
        logging.info('Wifi interface: {}, wifi driver: {}'.format(
            self.wireless.interface(), self.wireless.driver()))
        # keep running until we land on Mars
        # keep the contents of this loop short (limit to one cmd/status or one
        # status) so that we can quickly catch KeyboardInterrupt, SystemExit
        while 'people' != 'on Mars':
            # PRIORITY 1: send command for the current network on if possible
            command_set = Command.objects.filter(
                time_completed__isnull=True,
                camera__ssid__exact=self.wireless.current())
            if len(command_set) > 0:
                self.sendCommand(command_set[0])
                if self.shouldBeOn(command_set[0]):
                    # get the status now because it is cheap
                    self.getStatus(command_set[0].camera)
            else:
                # PRIORITY 2: send the oldest command still in the queue
                command_set = Command.objects.filter(
                    time_completed__isnull=True).order_by('-date_added')
                if len(command_set) > 0:
                    self.sendCommand(command_set[0])
                    if self.shouldBeOn(command_set[0]):
                        # get the status now because it is cheap
                        self.getStatus(command_set[0].camera)
                else:
                    # PRIORITY 3: check status of the most stale camera
                    camera_set = Camera.objects.all().order_by('last_attempt')
                    if len(camera_set) > 0:
                        self.getStatus(camera_set[0])

            # protect the cpu in the event that there was nothing to do
            time.sleep(0.1)


# run proxy if called directly
if __name__ == '__main__':
    proxy = GoProProxy()
    proxy.run()
