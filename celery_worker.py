import json
import logging
from os.path import exists, isfile, join

from celery.signals import after_setup_logger

from app import app
from tubee import celery

# Push flask context for celery
app.app_context().push()

# Setup celery logging config
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    external_config = join(app.instance_path, "logging_celery.cfg")
    if exists(external_config) and isfile(external_config):
        with open(external_config) as json_file:
            logging.config.dictConfig(json.load(json_file))
        logging.info("External Celery Config Loaded")
