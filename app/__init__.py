import quart.flask_patch
import os
from quart import Quart
# from flask_assets import Environment
# from flask_compress import Compress
from flask_login import LoginManager
from flask_mail import Mail
# from flask_rq import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_marshmallow import Marshmallow

# from app.assets import app_css, app_js, vendor_css, vendor_js
from config import config as Config

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
db = SQLAlchemy()
ma = Marshmallow()
csrf = CSRFProtect()
# TODO: Use quart-compress or nginx to compress the files for you
# compress = Compress()

# Set up Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'

UPLOAD_FOLDER = 'app/static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def create_app(config):
    app = Quart(__name__)
    config_name = config

    if not isinstance(config, str):
        config_name = os.getenv('QUART_CONFIG', 'default')

    app.config.from_object(Config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.config['RECAPTCHA_USE_SSL'] = False
    app.config['RECAPTCHA_PUBLIC_KEY'] = 'public'
    app.config['RECAPTCHA_PRIVATE_KEY'] = 'private'
    app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

    Config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    # TODO: See todo above.
    # compress.init_app(app)
    # TODO: Redis integration
    # RQ(app)

    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    # assets_env = Environment(app)
    # dirs = ['assets/styles', 'assets/scripts']
    # for path in dirs:
    #     assets_env.append_path(os.path.join(basedir, path))
    # assets_env.url_expire = True

    # assets_env.register('app_css', app_css)
    # assets_env.register('app_js', app_js)
    # assets_env.register('vendor_css', vendor_css)
    # assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .controllers import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .controllers import account as account_blueprint
    app.register_blueprint(account_blueprint)

    from .controllers import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app
