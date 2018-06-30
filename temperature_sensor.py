import logging
import time
import os
import random

logger = logging.getLogger(__name__)


class TemperatureSensor:
    def __init__(self, dev_id, rec_id):
        self.device_id = dev_id
        self.record_id = rec_id
        dev_path = os.path.join('/sys/bus/w1/devices', self.device_id, 'w1_slave')
        if not os.path.isfile(dev_path):
            raise IOError('Sensor could not be detected: {} at {}'.format(self, dev_path))
        self._device_file = dev_path
        self.last_read = None

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


class MockTemperatureSensor(TemperatureSensor):
    def __init__(self, dev_id, rec_id):
        self.device_id = dev_id
        self.record_id = rec_id
        self._device_file = None
        self.last_read = None
        self.mock_read_value = random.random

    def read(self):
        logger.debug('{} read {}.'.format(self, self.mock_read_value))
        self.last_read = time.time()
        if callable(self.mock_read_value):
            return self.mock_read_value()
        else:
            return self.mock_read_value

    def __repr__(self):
        return "MockTemperatureSensor {}".format(self.device_id)


def temperature_sensor_factory(temp_sensor_configs):
    temp_sensors = {}
    for temp_sensor_name in temp_sensor_configs:
        temp_sensor_data = temp_sensor_configs[temp_sensor_name]
        device_id = temp_sensor_data['DeviceID']
        recording_id = temp_sensor_data['RecordingID']

        if 'Mock' in temp_sensor_data.keys() and temp_sensor_data['Mock'] == 'True':
            temp_sensors[temp_sensor_name] = MockTemperatureSensor(device_id, recording_id)
        else:
            temp_sensors[temp_sensor_name] = TemperatureSensor(device_id, recording_id)
    return temp_sensors







