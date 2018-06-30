import logging
import time
from temperature_sensor import TemperatureSensor
logger = logging.getLogger(__name__)

class MockTemperatureSensor(TemperatureSensor):
    def __init__(self, dev_id, dev_file):
        self.device_id = dev_id
        self._device_file = dev_file
        self.last_read = None
        self.mock_read_value = None
        

    def read(self):
        logger.debug('{} read {}.'.format(self, self.mock_read_value, 2))
        self.last_read = time.time()
        return self.mock_read_value


    def __repr__(self):
        return "TemperatureSensor {}".format(self.device_id)
