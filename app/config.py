import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = False

    @staticmethod
    def init_app(app):
        pass

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV-DATABASE-URI') or \
        'sqlite:///{}'.format(os.path.join(basedir, 'dev-sqlite.db'))

class TestConfig(BaseConfig):
    TESTING = True
    MARSHMALLOW_STRICT = True
    MARSHMALLOW_DATEFORMAT = 'rfc'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST-DATABASE-URI') or \
        'sqlite:///{}'.format(os.path.join(basedir, 'test-sqlite.db'))

configs = {
    'dev'     : DevConfig,
    'testing' : TestConfig,
    'default' : DevConfig
    }
