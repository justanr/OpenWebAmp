from collections import namedtuple

from app import app, db, ma, models, serializers, utils
from flask.ext.script import Manager

manager = Manager(app)

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

if __name__ == "__main__":
    manager.run()
