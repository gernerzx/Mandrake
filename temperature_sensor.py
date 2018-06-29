import logging
import time
import pyinotify
logger = logging.getLogger(__name__)


class TemperatureSensor:
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CREATE(self, event):
            print("Creating:" + event.pathname)

        def process_IN_DELETE(self, event):
            print("Removing:" + event.pathname)

    def __init__(self, dev_id, dev_file):
        self.device_id = dev_id
        self._device_file = dev_file
        self.last_read = None
        self._wm = pyinotify.WatchManager()
        self._notifier = pyinotify.ThreadedNotifier(self._wm, self.EventHandler())
        self._watches = self._wm.add_watch('/tmp', pyinotify.IN_DELETE | pyinotify.IN_MODIFY, rec=True)
        self.notifier.start()

    def read(self):
        with open(self._device_file, 'r') as content_file:
            raw_data = content_file.read()
            lines = raw_data.split('\n')
            if len(lines) < 2:
                raise IOError('Failed to read from {}. Unidentified format!'.format(self))
            if lines[0].split(' ')[-1] != "YES":
                raise IOError('Read bad data from {}'.format(self))
            sensor_count = lines[1].split(' ')[-1].lstrip('t=')
            temp_c = float(sensor_count) / 1000.0
            temp_f = round(temp_c * 9.0 / 5.0 + 32.0, 2)
            
            logger.debug('{} read {}.'.format(self, temp_f, 2))
            self.last_read = time.time()
            return temp_f

    def __repr__(self):
        return "TemperatureSensor {}".format(self.device_id)

