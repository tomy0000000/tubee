"""Boot Script of Tubee"""
import os

import coverage

from tubee import create_app

cov = None
if os.environ.get("COVERAGE"):
    cov = coverage.coverage(branch=True, include="tubee/*", omit="tubee/tests/*")
    cov.start()


config = os.environ.get("CONFIG", "development")
app = create_app(config_name=config, coverage=cov)


if __name__ == "__main__":
    app.run()
