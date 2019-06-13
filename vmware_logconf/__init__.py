import logging

from logging.config import fileConfig

# setup logger
fileConfig("vmware_logconf/logging_config.ini")
logger = logging.getLogger()