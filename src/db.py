import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

from src.sequences import init_sequence_data


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_db():
    init_sequence_data(get_db())
