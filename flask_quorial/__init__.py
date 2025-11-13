# __init__.py
# last change 11 March 23
# - contains application factory
# - tells Python that the flaskr/ directory is a package
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    #create and configure the app
    # __name__ is name of current Python module
    # instance_relative_config=True tells app that config files are relative to instance folder
    app = Flask(__name__, instance_relative_config=True)

    #flask behind a proxy:
    # https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/?highlight=reverse%20proxy
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    app.config.from_mapping(
            # used by Flask to keep data safe
            # TODO: when deployed dev -> random value
            SECRET_KEY='dev',
            # path of sqlite database file
            DATABASE=os.path.join(app.instance_path,'flaskauu.sqlite'),
    )
    # flush needed as stdout is BUFFERED
    print('Database created...', flush=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_mapping(test_config)

    #ensure the instance folder exists - Flask does it not automatically
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize db
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # no url_prefix -> index view at
    from . import auu
    app.register_blueprint(auu.bp)
    app.add_url_rule('/', endpoint='index')

    # Removed exams and library blueprints for chat-only app

    from . import chat
    app.register_blueprint(chat.bp)

    return app
