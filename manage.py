#!/usr/bin/env python
import quart.flask_patch
import os
import subprocess

from quart.cli import with_appcontext
from flask_migrate import Migrate
# from redis import Redis
# from rq import Connection, Queue, Worker

from app import create_app, db
from app.models import Role, User
from config import Config

app = create_app(os.getenv('QUART_CONFIG') or 'default')
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

@app.cli.command("unittest")
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command("recreate_db")
@with_appcontext
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


"""
@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Number of each model type to create',
    dest='number_users')
"""
@app.cli.command("add_fake_data")
@with_appcontext
def add_fake_data():
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=20)


@app.cli.command("add_fake_users")
@with_appcontext
def add_fake_users():
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=20)


@app.cli.command("setup_dev")
@with_appcontext
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@app.cli.command("setup_prod")
@with_appcontext
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email=Config.ADMIN_EMAIL).first() is None:
            user = User(
                first_name='Admin',
                last_name='Account',
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL)
            db.session.add(user)
            db.session.commit()
            print('Added administrator {}'.format(user.full_name()))


@app.cli.command("run_worker")
@with_appcontext
def run_worker():
    """Initializes a slim rq task queue."""
    # TODO: Fix Redis integration
    #listen = ['default']
    #conn = Redis(
    #    host=app.config['RQ_DEFAULT_HOST'],
    #    port=app.config['RQ_DEFAULT_PORT'],
    #    db=0,
    #    password=app.config['RQ_DEFAULT_PASSWORD'])

    #with Connection(conn):
    #    worker = Worker(map(Queue, listen))
    #    worker.work()
    pass


@app.cli.command("format")
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
