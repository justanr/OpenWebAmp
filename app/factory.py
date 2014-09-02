from flask import Flask
from .config import configs

def create_app(env, exts=None):
    app = Flask(__name__)
    
    config = configs.get(env, 'default')
    
    app.config.from_object(config)
    config.init_app(app)

    if exts:
        for ext in exts:
            ext.init_app(app)

    return app
