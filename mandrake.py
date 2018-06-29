#!/usr/bin/python3
import os, time, requests, sys, datetime
from temperature_sensor import TemperatureSensor
import logging

mandrake_url = 'https://script.google.com/macros/s/AKfycbw5euftq51NMhMbY8QqloVmRdzq3r791jULNb2P0lPecNIfPEQ/exec'
interval = 60*15
logger = logging.getLogger(__name__)

def detectOneWireSensors():
    w1_root_path = "/sys/bus/w1/devices"
    devices = []
    for file_name in os.listdir( w1_root_path ):
        file_path = os.path.join( w1_root_path, file_name)
        if os.path.isdir( file_path ) and "w1_bus_master" not in file_name:
            device_path = os.path.join(file_path, "w1_slave")
            devices.append( TemperatureSensor( file_name, device_path ) )

    logger.debug( "Found {} onewire devices: \n\t{}".format( len(devices), '\n\t'.join([str(d) for d in devices])))
    return devices

def postToCloud( data, url ):
    pass
    #req = requests.get(url, params=data)
    #logger.debug('Request got {} to {}'.format( req.status_code, url ))



logging.basicConfig(level=logging.INFO)
sensors = detectOneWireSensors()
water_sensor_found = False
air_sensor_found = False
for sens in sensors:
    if( sens.device_id == '28-0218405755ff' ):
        logger.info("Water Temperature sensor found!")
        water_sensor_found = True
        water_sensor = sens

    if( sens.device_id == '28-0218405652ff' ):
        logger.info("Air Temperature sensor found!")
        air_sensor_found = True
        air_sensor = sens

if( not water_sensor_found ):
    logger.fatal('Failed to find water temperature sensor. Terminating!')
    sys.exit()
    
if( not air_sensor_found ):
    logger.fatal('Failed to find air temperature sensor. Terminating!')
    sys.exit()

while True:
    start_time = time.time()
    data = {}
    timestamp = datetime.datetime.now().isoformat()
    data['Timestamp'] = timestamp
    logging.info('Gathering data for: {}'.format( timestamp ))
    
    water_temp = water_sensor.read()
    air_temp = air_sensor.read()
    logger.info('>>> Temperatures: air={} water={}'.format( air_temp, water_temp ))
    
    data['Air Temperature'] = air_temp
    data['Water Temperature'] = water_temp
    
    postToCloud( data, mandrake_url )

    sleep_time = max(0, interval - (time.time() - start_time))
    logger.info('Sleeping {} to make an interval of {}'.format( sleep_time, interval))
    time.sleep( sleep_time )
