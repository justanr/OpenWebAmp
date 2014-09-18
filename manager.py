import unittest

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

config = configs['dev']

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

@manager.option('-d', '--dir', dest='dir')
def add(dir):
    utils.store_directory(dir)

@manager.shell
def _shell_context():
    return dict(
        app=app, 
        db=db, 
        ma=ma, 
        models=models, 
        schemas=schemas, 
        utils=utils
        )

@manager.command
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
