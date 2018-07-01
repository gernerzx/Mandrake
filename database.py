import peewee
import datetime
from mandrake_config import *
import os
import sys


def init_db():
    try:
        db_config = MandrakeConfig['DataLogging']['Database']
    except KeyError:
        logger.warning('No database connector initialized. Only an issue if you want to log data to a database.')
        return None
    try:
        location = db_config['Path']
    except KeyError:
        logger.fatal('Syntax Error in DataLogging:Database config. Database must contain a \'Path\' variable.')
        sys.exit(-1)
    if location.lower() == 'default':
        location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mandrake.sqlite')
    return peewee.SqliteDatabase(location)


MandrakeDatabase = init_db()


# TODO: Dynamically construct ORM classes based on known sensor types at runtime
class Water_Temperature(peewee.Model):
    """
    ORM model of the Water Temperature table
    """
    timestamp = peewee.DateTimeField()
    value = peewee.DoubleField()

    class Meta:
        database = MandrakeDatabase


class Air_Temperature(peewee.Model):
    """
    ORM model of the Air Temperature table
    """
    timestamp = peewee.DateTimeField()
    value = peewee.DoubleField()

    class Meta:
        database = MandrakeDatabase


if MandrakeDatabase:
    MandrakeDatabase.connect()
    # TODO: Dynamically create tables as needed
    MandrakeDatabase.create_tables([Air_Temperature, Water_Temperature])


def log_to_database(sensor_data):
    db_timestamp = datetime.datetime.now()
    for sensor_name in sensor_data:
        try:
            orm_obj = globals()[sensor_name]
            db_session = orm_obj.create(timestamp=db_timestamp, value=sensor_data[sensor_name])
            db_session.save()
            logger.debug('Data successfully saved to database: {}@{}->{}'.format(db_timestamp, sensor_name, sensor_data[sensor_name]))
        except KeyError:
            logger.error('ORM class for {} not defined!'.format(sensor_name))
            sys.exit(-1)
