#!/usr/bin/python

# logger.py
# Josh Villbrandt <josh@javconcepts.com>
# 2015/01/27


import argparse
import django
import logging
import json
import time
import sys
import os
from colorama import Fore

# import django models
sys.path.append('/home/GoProController')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GoProController.settings")
django.setup()
from GoProController.models import Camera


# make sure the cameras are always in the state we want them in
class GoProLogger:
    startTime = None
    updates = {}
    summaryMap = {
        'notfound': 0,
        'sleeping': 1,
        'on': 2,
        'recording': 3
    }

    # init
    def __init__(self, log_level=logging.INFO):
        # setup log
        log_format = '%(asctime)s   %(message)s'
        logging.basicConfig(format=log_format, level=log_level)

        # parse command line arguments
        parser = argparse.ArgumentParser(description=(
            'Create .csv files with GoPro data.'))
        parser.add_argument(
            '-i, --interval', dest='interval', type=int, default=1,
            help='the interval to query the database in seconds')
        parser.add_argument(
            '-d, --directory', dest='directory', required=True,
            help='the output directory for csv files')
        args = parser.parse_args()
        self.interval = args.interval
        self.directory = args.directory

    # report status of all cameras
    def checkForUpdates(self):
        cameras = Camera.objects.all()
        for camera in cameras:
            # generate filename
            filename = os.path.join(
                self.directory, '{}.csv'.format(camera.ssid))

            # has camera been updated?
            if camera.id not in self.updates:
                # this is the first time we've seen this camera!

                # delete old file
                if os.path.exists(filename):
                    os.unlink(filename)

                # write headers
                self.writeCsv(
                    filename,
                    ['time', 'status', 'batt1', 'batt2', 'batt'],
                    verbose=False)

                # log data
                self.writeCsv(filename, self.getFields(camera))
                self.updates[camera.id] = camera.last_update
            elif camera.last_update > self.updates[camera.id]:
                # log data
                self.writeCsv(filename, self.getFields(camera))
                self.updates[camera.id] = camera.last_update
            else:
                # this camera has not been updated
                pass

    # get fields for logging
    def getFields(self, camera):
        delta = camera.last_update - self.startTime
        fields = [delta.total_seconds(), self.summaryMap[camera.summary]]

        if camera.summary == 'on' or camera.summary == 'recording':
            status = json.loads(camera.status)
            fields = fields + [
                status['batt1'], status['batt2'],
                int(status['batt1']) + int(status['batt2'])]
        else:
            fields = fields + [0, 0, 0]

        return fields

    # append data to file
    def writeCsv(self, filename, fields, verbose=True):
        if verbose:
            logging.info('{}: {}'.format(filename, fields))

        str_fields = []
        for field in fields:
            str_fields.append(str(field))

        with open(filename, "a") as f:
            f.write(','.join(str_fields))
            f.write(os.linesep)

    # main loop
    def run(self):
        logging.info('{}GoProLogger.run(){}'.format(Fore.CYAN, Fore.RESET))
        logging.info('{}Update interval: {}s{}'.format(
            Fore.CYAN, self.interval, Fore.RESET))
        logging.info('{}Output directory: {}{}'.format(
            Fore.CYAN, self.directory, Fore.RESET))

        # make sure directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # get start time
        cameras = Camera.objects.all()
        for camera in cameras:
            if self.startTime is None or camera.last_update < self.startTime:
                self.startTime = camera.last_update

        # keep running until we land on Mars
        last = None
        while 'people' != 'on Mars':
            # check if we should run the spammer now or not
            now = time.time()
            if last is None or (now - last) > self.interval:
                last = now
                self.checkForUpdates()

            # protect the cpu in the event that there was nothing to do
            time.sleep(0.1)


# run if called directly
if __name__ == '__main__':
    logger = GoProLogger()
    logger.run()
