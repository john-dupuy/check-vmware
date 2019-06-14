import logging

from logging.config import fileConfig

# setup logger
fileConfig("/var/lib/shinken/libexec/vmware_logconf/logging_config.ini")
logger = logging.getLogger()