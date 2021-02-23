import sys

from alembic.config import Config
from alembic import command
from AuthService import settings


def drop_all(alembic_conf=None):
    """
    Drops all tables in the database.

    @:param alembic_conf: Alembic configuration to be used.
    """

    if alembic_conf is None:
        alembic_conf = initialize_alembic_conf()

    print("Dropping all tables in 'auth.models'..")

    from auth import models
    command.downgrade(alembic_conf, "base")

    print("SUCCESS")


def initialize_alembic_conf():
    """
    Initializes alembic configuration.
    """
    config = Config("alembic.ini")
    config.set_main_option('script_location', "alembic")
    config.set_main_option('sqlalchemy.url', settings.SQLALCHEMY_DB_URL)

    return config


def flush_db():
    """
    Clears the current database tables by dropping tables and creating new
    empty ones.
    """

    conf = initialize_alembic_conf()

    drop_all(conf)

    print("Upgrading migrations to head..")
    command.upgrade(conf, "head")
    print("SUCCESS")


def call_command():
    """
    Parses the system arguments to call the appropriate command.
    """
    commands = {
        "drop_all": drop_all,
        "flush_db": flush_db
    }
    if len(sys.argv) != 2:
        raise Exception(
            "Bad script usage. Example: python manage.py [command]"
        )

    command_name = sys.argv[1]
    if command_name not in commands:
        raise Exception(f"Unrecognized command '{command_name}'")

    commands[command_name]()


if __name__ == "__main__":
    call_command()
