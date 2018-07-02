#!/usr/bin/python3
import logging
from temperature_sensor import *
from mandrake_config import *
from pprint import pformat, pprint
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
    logger.debug('Collecting Sensor Data for {}'.format(', '.join(sensors_to_check.keys())))
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
        logger.info('Logged {} to {}'.format(', '.join(sensor_data.keys()), service_url))


def record_database(db_connector, sensor_data):
    db_timestamp = datetime.datetime.now()
    for sensor_name in sensor_data:
        try:
            orm_obj = getattr(database, sensor_name)
            db_session = orm_obj.create(timestamp=db_timestamp, value=sensor_data[sensor_name])
            db_session.save()
        except AttributeError:
            logger.error('ORM class for {} not defined!'.format(sensor_name))
            sys.exit(-1)
    logger.info('Logged {} sensors to {}'.format(', '.join(sensor_data.keys()), db_connector))


def sleep_iteration(start_time, cyc_rate):
    sleep_time = max(0, cyc_rate - int(time.time() - start_time))
    logger.debug('Sleeping {} to make an interval of {}'.format(sleep_time, rate))
    if sleep_time == 0:
        logger.warning('Not enough time to finish')
    thread_exit.wait(float(sleep_time))


def record_loop(rate, recorder, target, name):
    while not thread_exit.is_set():
        start_time = time.time()
        recorder(target, collect_sensor_data(sensors))
        sleep_iteration(start_time, rate)
        logger.info('Waking up {}'.format(name))
    logger.info("Shutting down {} recorder thread.".format(name))


# Main Code
sensors = initialize_sensors()
logger.info('Successfully Initialized: {}'.format(', '.join(sensors)))

recorder_threads = list()
recorder_config = MandrakeConfig['DataLogging']
thread_exit = threading.Event()
thread_exit.clear()
for recorder_type in recorder_config:
    if recorder_type == 'HTTP':
        try:
            for http_recorder_name in recorder_config[recorder_type]:
                http_recorder = recorder_config[recorder_type][http_recorder_name]
                req_url = http_recorder['URL']
                req_rate = http_recorder['Rate']
                recorder_threads.append(threading.Thread(target=record_loop,
                                        args=(req_rate, record_http_service, req_url, http_recorder)))
                logger.info('Successfully initialized {}:{} recorder'.format(recorder_type, http_recorder))
        except KeyError:
            logger.fatal('HTTP recorder configs must have the URL and Rate items')
            sys.exit(-1)

    elif recorder_type == 'Database':
        try:
            database_config = recorder_config[recorder_type]
            path = database_config['Path']
            if path.lower() == 'default':
                path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mandrake.sqlite')
            rate = database_config['Rate']
            recorder_threads.append(threading.Thread(target=record_loop,
                                    args=(rate, record_database, path, recorder_type)))
            logger.info('Successfully initialized Database recorder')
        except KeyError:
            logger.fatal('Database recorder must have the Path and Rate items')

    else:
        logger.error('Unsupported data logging type: {}'.format(recorder_type))

for thread in recorder_threads:
    thread.start()

try:
    for thread in recorder_threads:
        thread.join()
except KeyboardInterrupt:
    logger.info('Shutting down threads!')
    thread_exit.set()
for thread in recorder_threads:
    thread.join()
logger.info('Mandrake Shutdown Complete!')
