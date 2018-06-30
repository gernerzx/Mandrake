import os
import requests
import logging
import time
from database import *
logger = logging.getLogger(__name__)





def configure_database():
    database = peewee.SqliteDatabase("mandrake.sqlite")
    database.connect()
    database.create_tables([AirTemperature, WaterTemperature])


def write_to_database(sens_data):
    at = AirTemperature.create( temperature = sens_data['Air Temperature'], sensor_id = '28-0218405652ff')
    at.save()
    wt = WaterTemperature.create( temperature = sens_data['Water Temperature'], sensor_id = '28-0218405755ff')
    wt.save()


