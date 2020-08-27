"""Boot Script of Tubee"""
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage

    COV = coverage.coverage(branch=True, include="tubee/*", omit="tubee/tests/*")
    COV.start()

import sys
import click
from flask_migrate import Migrate, upgrade
from tubee import create_app, db
from tubee.models import (
    Action,
    Callback,
    Channel,
    Notification,
    Subscription,
    SubscriptionTag,
    Tag,
    User,
    Video,
)

config = os.environ.get("FLASK_ENV", "default")
app = create_app(config)
migrate = Migrate()
with app.app_context():
    migrate.init_app(app, db, render_as_batch=True)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        Action=Action,
        Callback=Callback,
        Channel=Channel,
        Notification=Notification,
        Subscription=Subscription,
        SubscriptionTag=SubscriptionTag,
        Tag=Tag,
        User=User,
        Video=Video,
    )


@app.cli.command()
@click.option(
    "--coverage/--no-coverage", default=False, help="Run tests under code coverage."
)
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import subprocess

        os.environ["FLASK_COVERAGE"] = "1"
        sys.exit(subprocess.call(sys.argv))

    import unittest

    tests = unittest.TestLoader().discover("tubee/tests")
    results = unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "htmlcov")
        COV.html_report(directory=covdir)
        print(f"HTML version: file://{covdir}/index.html")
    sys.exit(not results.wasSuccessful())


# @app.cli.command()
# @click.option("--length", default=25,
#               help="Number of functions to include in the profiler report.")
# @click.option("--profile-dir", default=None,
#               help="Directory where profiler data files are saved.")
# def profile(length, profile_dir):
#     """Start the application under the code profiler."""
#     from werkzeug.contrib.profiler import ProfilerMiddleware
#     app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
#                                       profile_dir=profile_dir)
#     app.run()


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()


if __name__ == "__main__":
    app.run()
