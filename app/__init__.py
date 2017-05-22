from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from lib.cache import build_cache_from_config


db = SQLAlchemy()
auth = HTTPBasicAuth()


def init_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config.from_pyfile('../settings/test.cfg')
    else:
        app.config.from_pyfile('../settings/default.cfg')
        # $ export APP_CONFIG = path/to/config/file
        app.config.from_envvar('APP_CONFIG', silent=True)

    global cache
    cache = build_cache_from_config(app)
    cache.init_app(app)

    db.init_app(app)

    # blueprints
    from app.api.users.users import users
    app.register_blueprint(users)

    return app
