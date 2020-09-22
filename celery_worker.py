import json
import logging
from os import path

from app import app
from tubee import celery

# Push flask context for celery
app.app_context().push()

# Setup celery logging config
external_config = path.join(app.instance_path, "logging_celery.cfg")
load_external = path.exists(external_config) and path.isfile(external_config)
if load_external:
    with open(external_config) as json_file:
        logging.config.dictConfig(json.load(json_file))
