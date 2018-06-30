import os
import requests
import logging
import time
from models import *
logger = logging.getLogger(__name__)

def detect_one_wire_sensors():
    w1_root_path = "/sys/bus/w1/devices"
    devices = []
    for file_name in os.listdir( w1_root_path ):
        file_path = os.path.join( w1_root_path, file_name)
        if os.path.isdir( file_path ) and "w1_bus_master" not in file_name:
            device_path = os.path.join(file_path, "w1_slave")
            devices.append( TemperatureSensor( file_name, device_path ) )

    logger.debug( "Found {} onewire devices: \n\t{}".format( len(devices), '\n\t'.join([str(d) for d in devices])))
    return devices


def post_to_gsheets(req_data, url):
    req_data['Timestamp'] = time.time()
    req = requests.get(url, params=req_data)
    logger.debug('Request got {} to {}'.format(req.status_code, url))


def write_to_database(sens_data):
    at = AirTemperature.create( temperature = sens_data['Air Temperature'], sensor_id = '28-0218405652ff')
    at.save()
    wt = WaterTemperature.create( temperature = sens_data['Water Temperature'], sensor_id = '28-0218405755ff')
    wt.save()

def collect_sensor_data(water_sensor, air_sensor):
    data = {}
    
    water_temp = water_sensor.read()
    air_temp = air_sensor.read()
    logger.info('Temperatures: air={} water={}'.format( air_temp, water_temp ))
    
    data['Air Temperature'] = air_temp
    data['Water Temperature'] = water_temp
    return data
