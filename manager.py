from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from app import app, db, ma, models, serializers, utils

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
        serials=serializers, 
        utils=utils
        )

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
