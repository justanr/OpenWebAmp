from flask import Flask


def create_app(package_name, config, exts=None):
    app = Flask(package_name)
    app.config.from_object(config)
    config.init_app(app)

    if exts:
        for ext in exts:
            ext.init_app(app)
    
    return app
