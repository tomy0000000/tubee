"""Boot Script of Tubee"""
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage
    COV = coverage.coverage(branch=True, include="tubee/*")
    COV.start()

import sys
import click
from flask_migrate import Migrate, upgrade
from tubee import create_app, db
from tubee.models import User

app = create_app(os.getenv("FLASK_ENV") or "default")
migrate = Migrate()
with app.app_context():
    migrate.init_app(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

@app.cli.command()
@click.option("--coverage/--no-coverage", default=False,
              help="Run tests under code coverage.")
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        import subprocess
        os.environ["FLASK_COVERAGE"] = "1"
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover("tests")
    results = unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "htmlcov")
        COV.html_report(directory=covdir)
        print("HTML version: file://%s/index.html" % covdir)
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
