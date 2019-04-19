"""uWSGI - Middleware between Flask and nginx"""
import codecs
import os
import sys
import logging
from werkzeug.debug import DebuggedApplication
logging.basicConfig(stream=sys.stderr)
os.environ["WERKZEUG_DEBUG_PIN"] = "off"

from Tubee import app
# app.debug = True
# app = DebuggedApplication(app, evalex=True)

if __name__ == "__main__":
    app.run()
