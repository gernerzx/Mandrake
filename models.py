#!/usr/bin/python3

# models.py
import peewee
import datetime

database = peewee.SqliteDatabase("mandrake.sqlite")


class WaterTemperature(peewee.Model):
    """
    ORM model of the Water Temperature table
    """
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    temperature = peewee.DoubleField()
    sensor_id = peewee.TextField()
 
    class Meta:
        database = database


class AirTemperature(peewee.Model):
    """
    ORM model of Air Temperature table
    """
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    temperature = peewee.DoubleField()
    sensor_id = peewee.TextField()
  
    class Meta:
        database = database
