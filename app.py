"""Boot Script of Tubee"""

import os

from coverage import Coverage

from tubee import create_app

coverage = None
if os.environ.get("COVERAGE"):
    coverage = Coverage(branch=True, include="tubee/*", omit="tubee/tests/*")
    coverage.start()


config = os.environ.get("CONFIG", "development")
app = create_app(config_name=config, coverage=coverage)


if __name__ == "__main__":
    app.run()
