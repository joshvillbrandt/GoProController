#!/usr/bin/python

# force.py
# Josh Villbrandt <josh@javconcepts.com>
# 2015/01/26


import argparse
import django
import logging
import copy
import time
import sys
import os
from colorama import Fore

# import django models
sys.path.append('/home/GoProController')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GoProController.settings")
django.setup()
from GoProController.models import Camera, Command


# make sure the cameras are always in the state we want them in
class GoProSpammer:
    maxRetries = 3
    status = None

    # init
    def __init__(self, log_level=logging.INFO):
        # setup log
        log_file = '/var/log/gopro-spammer.log'
        log_format = '%(asctime)s   %(message)s'
        logging.basicConfig(format=log_format, level=log_level)

        # file logging
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(log_format))
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(fh)

        # parse command line arguments
        parser = argparse.ArgumentParser(description=(
            'Automatically re-issue GoPro commands as needed.'))
        parser.add_argument(
            '-i, --interval', dest='interval', type=int, default=1,
            help='the interval to query the database in seconds')
        parser.add_argument(
            '-p, --param', dest='param',
            help='the parameter to be changed or "status" for status')
        parser.add_argument(
            '-v, --value', dest='value',
            help='the value to set the parameter to')
        args = parser.parse_args()
        self.interval = args.interval
        self.param = args.param
        self.value = args.value

    # spam the command
    def spam(self):
        if self.param is not 'status':
            queued_commands = Command.objects.filter(
                time_completed__isnull=True,
                camera__ssid__exact=self.wireless.current())

            # only add another round of commands if command queue is empty
            if len(command_set) == 0:
                logging.info('{}{} {}={}{}'.format(
                    Fore.CYAN,
                    'Empty command queue; spamming',
                    self.param,
                    self.value,
                    Fore.RESET))
                cameras = Camera.objects.all()
                for camera in cameras:
                    # create a command just for this camera
                    command = Command(
                        camera=camera, command=self.param, value=self.value)
                    command.save()

    # report status of all cameras
    def getStatus(self):
        status = {}
        # get status of all cameras
        cameras = Camera.objects.all()
        for camera in cameras:
            # we only care about power and record here
            if power in camera.status and camera.status['power'] == 'on':
                pass
            else:
                status[camera.ssid] = 'off'

        return status

    # report status of all cameras
    def printStatus(self):
        # color statuses
        colored_status = copy.deepcopy(self.status)
        for ssid, status in colored_status.iter_items():
            color = None

            if status == 'record':
                color = Fore.RED
            elif status == 'on':
                color = Fore.GREEN
            elif status == 'sleeping':
                color = Fore.YELLOW
            else:
                color = Fore.RESET

            colored_status[ssid] = '{}{}{}'.format(
                color, status, Fore.RESET)

        # now print
        logging.info('Status: {}'.format(colored_status.join(',')))

    # report status of all cameras
    def status(self):
        # get status
        status = self.getStatus()

        # print if different
        if status != self.status:
            self.status = status
            self.printStatus()

    # main loop
    def run(self):
        logging.info('{}GoProSpammer.run(){}'.format(Fore.GREEN, Fore.RESET))
        logging.info('Interval: {}'.format(self.interval))

        # keep running until we land on Mars
        last = None
        while 'people' != 'on Mars':
            # check if we should run the spammer now or not
            now = time.time()
            print(now, last)
            if last is None or (now - last) > self.interval:
                last = now
                self.spam()
                self.status()

            # protect the cpu in the event that there was nothing to do
            time.sleep(0.1)


# run spammer if called directly
if __name__ == '__main__':
    spammer = GoProSpammer()
    spammer.run()
