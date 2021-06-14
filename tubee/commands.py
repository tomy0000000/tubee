import os
import subprocess
import sys
import unittest

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext

from tubee import db, models
from tubee.helper import setup_app

docker_cli = AppGroup("docker", help="Run application with docker-compose.")


def make_shell_context():
    return dict(db=db, models=models)


@click.command()
@with_appcontext
def deploy():
    """Run deployment tasks."""
    setup_app()


@click.command()
@click.option(
    "--coverage/--no-coverage",
    "run_converage",
    default=False,
    help="Run tests under code coverage.",
)
@with_appcontext
def test(run_converage):
    """Run the unit tests."""
    if run_converage and not os.environ.get("FLASK_COVERAGE"):
        os.environ["FLASK_COVERAGE"] = "1"
        sys.exit(subprocess.call(sys.argv))

    tests = unittest.TestLoader().discover("tubee/tests")
    results = unittest.TextTestRunner(verbosity=2).run(tests)

    if os.environ.get("FLASK_COVERAGE"):
        current_app.coverage.stop()
        current_app.coverage.save()
        print("Coverage Summary:")
        current_app.coverage.report()
        covdir = os.path.join(os.path.dirname(__file__), "..", "htmlcov")
        covdir_abs = os.path.abspath(covdir)
        current_app.coverage.html_report(directory=covdir_abs)
        print(f"HTML version: file://{covdir_abs}/index.html")
    sys.exit(not results.wasSuccessful())


@docker_cli.command(
    "up", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option(
    "--dev/--prod",
    "development",
    default=True,
    help="Application mode.  [default: dev]",
)
@click.pass_context
def docker(context, development):
    """Run Development Application"""
    command = ["docker-compose"]
    setup_app()
    if development:
        command += "--file docker-compose.dev.yml".split()
        command.append("up")
        command += context.args
        proc = subprocess.run(command)
        if proc.returncode != 0:
            sys.exit(1)
        sys.exit(subprocess.run(["flask", "run"]).returncode)
    else:
        command.append("up")
        command += context.args
        sys.exit(subprocess.run(command).returncode)
