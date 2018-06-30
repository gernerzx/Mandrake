import platform
import os
import logging
import yaml
import sys
logger = logging.getLogger(__name__)

try:
    _config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cfg', 'config-{}.yml'.format(platform.node()))
    with open(_config_file_path, 'r') as yml_file:
        MandrakeConfig = yaml.load(yml_file)

except FileNotFoundError:
    logger.fatal('Config file not found: {}'.format(_config_file_path))
    sys.exit(-1)
