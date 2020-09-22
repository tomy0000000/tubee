"""Boot Script of Tubee"""
import os

import coverage
from dotenv import load_dotenv

from tubee import create_app

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

cov = None
if os.environ.get("FLASK_COVERAGE"):
    cov = coverage.coverage(branch=True, include="tubee/*", omit="tubee/tests/*")
    cov.start()


config = os.environ.get("FLASK_ENV", "default")
app = create_app(config, coverage=cov)


if __name__ == "__main__":
    app.run()
