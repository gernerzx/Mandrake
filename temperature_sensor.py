import logging
logger = logging.getLogger(__name__)

class TemperatureSensor():
    def __init__( self, dev_id, dev_file ):
        self.device_id = dev_id
        self._device_file = dev_file
        self.last_read = None
        self.rate = 10

    def read( self ):
        with open(self._device_file, 'r') as content_file:
            raw_data = content_file.read()
            lines = raw_data.split('\n')
            if( len(lines) < 2 ):
                raise IOError('Failed to read from {}. Unidentified format!'.format( self ))
            if( lines[0].split(' ')[-1] != "YES" ):
                raise IOError('Read bad data from {}'.format( self ))
            sensor_count = lines[1].split(' ')[-1].lstrip('t=')
            temp_c = float(sensor_count) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            
            logger.debug('{} read {}.'.format( self, temp_f ))
            return temp_f
            

    def __repr__( self ):
        return "TemperatureSensor {}".format( self.device_id ) 

