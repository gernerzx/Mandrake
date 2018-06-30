#!/usr/bin/python3
import logging
from temperature_sensor import *
from mandrake_config import *
from database import *
import requests
import argparse

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Set log level ot debugging.", action="store_true")
args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def initialize_sensors():
    sensor_config = MandrakeConfig['Sensors']
    sensors_data = {}
    for sensor_type in sensor_config:
        if sensor_type == 'Temperature':
            sensors_data.update(temperature_sensor_factory(sensor_config['Temperature']))
        else:
            raise NotImplementedError("Sensor of type {} not supported!".format(sensor_type))
    return sensors_data


def collect_sensor_data(sensors_to_check):
    results = {}
    logger.info('Collecting Sensor Data for {}'.format(', '.join(sensors_to_check.keys())))
    for sensor_key in sensors_to_check.keys():
        sensor = sensors_to_check[sensor_key]
        results[sensor.record_id] = sensor.read()
        logger.info('Read {} from {}'.format(results[sensor.record_id], sensor))
    return results


def post_data(req_data, req_url):
    req_data['Timestamp'] = time.time()
    req = requests.get(req_url, params=req_data)
    if not req.status_code == 200:
        logger.error('Request got {} to {}'.format(req.status_code, req_url))
    else:
        logger.debug('HTTP data logging request got {} to {}'.format(req.status_code, req_url))


def record_data(sensor_data):
    try:
        recording_config = MandrakeConfig['DataLogging']
    except KeyError:
        return
    log_locations = ""
    for record_type in recording_config:
        if record_type == 'HTTP':
            try:
                for http_record in recording_config[record_type]:
                    log_locations += http_record
                    url = recording_config[record_type][http_record]['URL']
                    post_data(sensor_data, url)
            except KeyError:
                logger.error('Syntax error in the DataLogging:HTTP config. Ignoring!')

        elif record_type == 'Database':
            log_locations += 'Database'
            try:
                log_to_database(sensor_data)
            except KeyError:
                logger.error('Syntax error in the DataLogging:Database config. Ignoring!')

        else:
            raise NotImplementedError('DataLogging type {} not supported!'.format(record_type))
    logger.info('Logged data to {}.'.format(log_locations))


def sleep_iteration(start):
    interval = MandrakeConfig['General']['Interval']
    sleep_time = max(0, interval - int(time.time() - start))
    logger.debug('Sleeping {} to make an interval of {}'.format(sleep_time, interval))
    if sleep_time == 0:
        logger.warning('Not enough time to finish')
    time.sleep(sleep_time)


sensors = initialize_sensors()
logger.info('Successfully Initialized: {}'.format(', '.join(sensors)))

logger.info('Entering Polling Loop...')
try:
    while True:
        start_time = time.time()
        data = collect_sensor_data(sensors)
        record_data(data)
        sleep_iteration(start_time)
except KeyboardInterrupt:
    pass
