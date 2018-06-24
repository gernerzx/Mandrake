#!/usr/bin/python3
import os, time
from temperature_sensor import TemperatureSensor
import logging

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



logging.basicConfig(level=logging.DEBUG)
sensors = detectOneWireSensors()
while (True):
    for sens in sensors:
        print(sens.read())
    time.sleep(1)
