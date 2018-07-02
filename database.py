import peewee
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



