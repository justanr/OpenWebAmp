from flask import Flask


def create_app(package_name, config, blueprints=None, exts=None):
    app = Flask(package_name)
    app.config.from_object(config)
    config.init_app(app)

    if blueprints:
        for bp in blueprints:
            app.register_blueprint(bp)

    if exts:
        for ext in exts:
            ext.init_app(app)
    
    return app
