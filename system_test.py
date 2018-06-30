#!/usr/bin/python3
import time
import sys
import logging
from mock_temperature_sensor import MockTemperatureSensor
from mandrake_utils import *
from models import *
import peewee

mandrake_url = 'https://script.google.com/macros/s/AKfycbw5euftq51NMhMbY8QqloVmRdzq3r791jULNb2P0lPecNIfPEQ/exec'
interval = 10
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

sensors = [MockTemperatureSensor('28-0218405755ff', None), MockTemperatureSensor('28-0218405652ff', None)]

for sens in sensors:
    if sens.device_id == '28-0218405755ff':
        logger.info("Water Temperature sensor found!")
        water_sensor_found = True
        water_sensor = sens

    if sens.device_id == '28-0218405652ff':
        logger.info("Air Temperature sensor found!")
        air_sensor_found = True
        air_sensor = sens

if not water_sensor_found:
    logger.fatal('Failed to find water temperature sensor. Terminating!')
if not air_sensor_found:
    logger.fatal('Failed to find air temperature sensor. Terminating!')
if not all([water_sensor_found, air_sensor_found]):
    sys.exit(-1)


air_sensor.mock_read_value = 95.2
water_sensor.mock_read_value = 90.7


database = peewee.SqliteDatabase("mandrake.sqlite")
database.connect()
database.create_tables([AirTemperature, WaterTemperature])

while True:
    start_time = time.time()
    
    data = collect_sensor_data( water_sensor, air_sensor)
    write_to_database(data)
    #post_to_gsheets(data, mandrake_url)
    

    sleep_time = max(0, interval - int(time.time() - start_time))
    logger.debug('Sleeping {} to make an interval of {}'.format(sleep_time, interval))
    time.sleep(sleep_time)
