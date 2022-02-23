import datetime
import flask
import flask_sqlalchemy
import flask_login
import json
import os

from .lib.models import db, Account
from .lib import helpers


class AnonymousUser:
    def get_id(self):
        return None

    def get_owner_id(self):
        return None

    def get_team_id(self):
        return None

    def is_active(self):
        return True

    def is_admin(self):
        return False

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False


def create_app(config_path):
    thisdir = os.path.dirname(__file__)
    app     = flask.Flask('decompetition',
        template_folder = os.path.join(thisdir, 'templates'),
        static_folder   = os.path.join(thisdir, 'static')
    )

    with open(config_path) as file:
        config = json.load(file)

        start = config.get('start')
        if start is not None:
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
            app.config['START_TIME'] = start.replace(tzinfo=datetime.timezone.utc)

        stop = config.get('stop')
        if stop is not None:
            stop = datetime.datetime.strptime(stop, '%Y-%m-%d %H:%M')
            app.config['END_TIME'] = stop.replace(tzinfo=datetime.timezone.utc)

        app.config['DEBUG']            = config['debug']
        app.config['DEVELOPMENT']      = config['development']
        app.config['TESTING']          = config['testing']
        app.config['WTF_CSRF_ENABLED'] = config['csrf']

        app.config['SQLALCHEMY_DATABASE_URI'] = config['database']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = config['secret_key']

    login_manager = flask_login.LoginManager()
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def user_loader(id):
        return Account.query.filter_by(id=id, user=True).first()

    login_manager.init_app(app)
    helpers.init_app(app)
    db.init_app(app)

    app.db = db

    with app.app_context():
        from .web.challenges.routes import blueprint as cbp
        app.register_blueprint(cbp)

        from .web.login.routes import blueprint as lbp
        app.register_blueprint(lbp)

        from .web.scores.routes import blueprint as sbp
        app.register_blueprint(sbp)

        from .web.teams.routes import blueprint as tbp
        app.register_blueprint(tbp)

        from .web.users.routes import blueprint as ubp
        app.register_blueprint(ubp)

        @app.route('/')
        def root():
            return flask.render_template('main.html')

        # db.create_all()
    return app
