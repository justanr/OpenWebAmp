from __future__ import print_function

import os
import unittest
import sys

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from app import (
    # extensions
    api, db, ma,

    # factory methods
    create_app, 

    # configuration
    configs, 

    # needed modules
    models, schemas, utils,

    # blueprints
    Stream
    )

from app.utils import shell


config = os.environ.get('OWA_ENV')
config = configs.get(config, 'default')


exts = [api, db, ma]
bps = [Stream]

app = create_app(
    __name__, 
    config, 
    exts=exts,
    blueprints=bps
    )

manager = Manager(app)
migrate = Migrate(app, db)

@manager.option('-n', '--name', dest='name')
@manager.option('-e', '--email', dest='email')
@manager.option('-p', '-pass', dest='password')
def member(name, email, password):
    member = models.Member.find_or_create(
        db.session,
        name=name,
        email=email,
        password=password
        )
    db.session.commit()
    print("Created member {}".format(name))

@manager.option('-d', '--dir', dest='dir')
@manager.option('-m', '--member', dest='member')
def add(dir, member=None):

    if member:
        member = models.Member.query.filter_by(name=member).one()

    try:
        shell.store_directory(dir, member)
    except (KeyboardInterrupt, EOFError) as e:
        db.session.rollback()
        sys.exit(1)
    else:
        sys.exit(0)

@manager.shell
def _shell_context():
    return dict(
        app=app, 
        db=db, 
        ma=ma, 
        models=models, 
        schemas=schemas, 
        utils=utils,
        config=config
        )

@manager.command
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
