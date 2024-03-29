import os
import subprocess
import sys
import unittest
from pathlib import Path

import click
from flask import current_app  # type: ignore
from flask.cli import with_appcontext

from .. import Tubee, db, models
from . import setup_app

current_app: Tubee

__all__ = ["deploy", "test", "admin"]


@click.command()
@with_appcontext
def deploy():
    """Run deployment tasks."""
    setup_app()


@click.command()
@click.option(
    "--coverage/--no-coverage",
    "coverage",
    default=False,
)
@with_appcontext
def test(coverage: bool):
    """Run the unit tests (with or withour coverage)."""
    if os.environ.get("CONFIG") != "testing":
        os.environ["CONFIG"] = "testing"
        if coverage:
            os.environ["COVERAGE"] = "True"
        sys.exit(subprocess.call([sys.executable, "-m", "flask"] + sys.argv[1:]))

    tests = unittest.TestLoader().discover("tests")
    results = unittest.TextTestRunner(verbosity=2).run(tests)

    if current_app.coverage:
        current_app.coverage.stop()
        current_app.coverage.save()

        click.echo("Coverage Summary:")
        current_app.coverage.report()

        html_covdir = Path.cwd().joinpath("htmlcov")
        current_app.coverage.html_report(directory=str(html_covdir))
        click.echo(f"HTML version: {html_covdir.joinpath('index.html').as_uri()}")

        xml_cov = Path.cwd().joinpath("coverage.xml")
        current_app.coverage.xml_report(outfile=xml_cov)
        click.echo(f"XML version: {xml_cov.as_uri()}")
    sys.exit(not results.wasSuccessful())


@click.command()
@click.argument("username")
@with_appcontext
def admin(username):
    """Grant user as admin."""
    user = models.User.query.get(username)
    if not user:
        raise ValueError(f"User <{username}> not found.")
    user.admin = True
    db.session.commit()
    click.echo(f"User <{username}> is now an admin.")
