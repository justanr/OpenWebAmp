import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = False

    MARSHMALLOW_STRICT = True
    MARSHMALLOW_DATEFORMAT = 'rfc'

    @staticmethod
    def init_app(app):
        pass

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'sqlite:///{}'.format(os.path.join(basedir, 'dev-sqlite.db'))

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
        'sqlite:///{}'.format(os.path.join(basedir, 'test-sqlite.db'))

class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI') or \
        'sqlite:///{}'.format(os.path.join(basedir, 'why-is-prod-here.db'))


configs = {
    'dev'     : DevConfig,
    'testing' : TestConfig,
    'prod'    : ProdConfig,
    'default' : DevConfig
    }
