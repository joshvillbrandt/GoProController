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
    statuses = None

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
        # parser.add_argument(
        #     '-f, --file', dest='file',
        #     help='a timeline file with each line as "time, param, value"')
        # parser.add_argument(
        #     '-t, --time', dest='time', type=int,
        #     help='elapsed time at init in seconds; ' +
        #     'defaults to the lowest time in --file')
        args = parser.parse_args()
        self.interval = args.interval
        self.param = args.param
        self.value = args.value
        # self.file = args.file
        # self.time = args.time

    # spam the command
    def spam(self):
        if self.param is not None and self.param is not 'status':
            queued_commands = Command.objects.filter(
                time_completed__isnull=True)

            # only add another round of commands if command queue is empty
            if len(queued_commands) == 0:
                logging.info('{}{} "{}={}"{}'.format(
                    Fore.RESET,
                    'Command queue empty; setting',
                    self.param,
                    self.value,
                    Fore.RESET))
                cameras = Camera.objects.all()
                for camera in cameras:
                    param = self.param
                    value = self.value

                    # override the command if the camera isn't powered on
                    if self.param != 'power' and (
                            camera.summary != 'on' and
                            camera.summary != 'recording'):
                        param = 'power'
                        value = 'on'

                    # create a command just for this camera
                    command = Command(
                        camera=camera, command=param, value=value)
                    command.save()

    # report status of all cameras
    def getStatus(self):
        statuses = []
        cameras = Camera.objects.order_by('ssid')
        for camera in cameras:
            statuses.append([camera.ssid, camera.summary])

        return statuses

    # report status of all cameras
    def printStatus(self):
        # color statuses
        colored = []
        for group in self.statuses:
            ssid = group[0]
            status = group[1]
            color = None

            if status == 'recording':
                color = Fore.RED
            elif status == 'on':
                color = Fore.GREEN
            elif status == 'sleeping':
                color = Fore.YELLOW
            else:
                color = Fore.RESET

            colored.append('{}{}{}'.format(
                color, ssid, Fore.RESET))

        # now print
        logging.info('Status change: {}'.format(', '.join(colored)))

    # report status of all cameras
    def status(self):
        # get status
        statuses = self.getStatus()

        # print if different
        if statuses != self.statuses:
            self.statuses = statuses
            self.printStatus()

    # main loop
    def run(self):
        logging.info('{}GoProSpammer.run(){}'.format(Fore.CYAN, Fore.RESET))
        logging.info('{}Update interval: {}s{}'.format(
            Fore.CYAN, self.interval, Fore.RESET))
        logging.info('{}Status meanings: {}{}, {}{}, {}{}, {}{}'.format(
            Fore.CYAN,
            Fore.YELLOW, 'sleeping',
            Fore.GREEN, 'on',
            Fore.RED, 'recording',
            Fore.RESET, 'notfound'))

        # keep running until we land on Mars
        last = None
        while 'people' != 'on Mars':
            # check if we should run the spammer now or not
            now = time.time()
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
