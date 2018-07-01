#!/usr/bin/python3
import logging
from temperature_sensor import *
from mandrake_config import *
from pprint import pformat
import database
import requests
import argparse
import threading
import datetime

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


def record_http_service(service_url, sensor_data):
    sensor_data['Timestamp'] = time.time()
    req = requests.get(service_url, params=sensor_data)
    if not req.status_code == 200:
        logger.error('Request got {} to {}'.format(req.status_code, service_url))
    else:
        logger.debug('HTTP data logging request got {} to {}'.format(req.status_code, service_url))
        logger.info('Logged {}@{} to {}'.format(sensor_data['Timestamp'],
                                                pformat(zip(sensor_data.keys(), sensor_data.values())),
                                                service_url))


def record_database(db_connector, sensor_data):
    db_timestamp = datetime.datetime.now()
    for sensor_name in sensor_data:
        try:
            orm_obj = getattr(database, sensor_name)
            db_session = orm_obj.create(timestamp=db_timestamp, value=sensor_data[sensor_name])
            db_session.save()
            logger.info('Logged {}@{}->{} to {}'.format(db_timestamp, sensor_name, sensor_data[sensor_name], db_connector))
        except AttributeError:
            logger.error('ORM class for {} not defined!'.format(sensor_name))
            sys.exit(-1)


def sleep_iteration(rate, interval):
    sleep_time = max(0, interval - int(time.time() - rate))
    logger.debug('Sleeping {} to make an interval of {}'.format(sleep_time, interval))
    if sleep_time == 0:
        logger.warning('Not enough time to finish')
    time.sleep(sleep_time)


def record_loop(rate, recorder, target):
    this_thread = threading.currentThread()
    while getattr(this_thread, "continue_execution", True):
        start_time = time.time()
        recorder(target, collect_sensor_data(sensors))
        sleep_iteration(start_time, rate)
    logger.info("Shutting down Recorder:{}:{} thread.".format(recorder, target))


# Main Code
sensors = initialize_sensors()
logger.info('Successfully Initialized: {}'.format(', '.join(sensors)))

try:
    recorder_threads = []
    recorder_threads.append(threading.Thread(target=record_loop, args=(10, record_database, database.MandrakeDatabase)))

    for thread in recorder_threads:
        thread.start()
    for thread in recorder_threads:
        thread.join()
except KeyboardInterrupt:
    logger.info('Shutting down threads!')
    for thread in recorder_threads:
        thread.continue_execution = False
    for thread in recorder_threads:
        thread.join()
