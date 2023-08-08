import os

from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException
from flask_migrate import Migrate
from flask_mail import Mail
from app.controllers.s3_bucket import S3Bucket

from app.logger import log
from .database import db, AnonymousUser

# instantiate extensions
login_manager = LoginManager()
migration = Migrate()
mail = Mail()
s3bucket = S3Bucket()


def create_app(environment="development"):
    from config import config
    from app.views import (
        main_blueprint,
        auth_blueprint,
        admin_blueprint,
        client_blueprint,
        case_blueprint,
        quiz_blueprint,
        stack_blueprint,
        candidate_blueprint,
        action_blueprint,
    )
    from app.common import models as m

    # Instantiate app.
    app = Flask(__name__)

    # Set app config.
    env = os.environ.get("APP_ENV", environment)
    configuration = config(env)
    app.config.from_object(configuration)
    configuration.configure(app)
    log(log.INFO, "Configuration: [%s]", configuration.ENV)

    # Set up extensions.
    db.init_app(app)
    migration.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    s3bucket.init_app(app)

    # Register blueprints.
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(client_blueprint)
    app.register_blueprint(case_blueprint)
    app.register_blueprint(quiz_blueprint)
    app.register_blueprint(stack_blueprint)
    app.register_blueprint(candidate_blueprint)
    app.register_blueprint(action_blueprint)

    # Set up flask login.
    @login_manager.user_loader
    def get_user(id: int):
        query = m.SuperUser.select().where(m.SuperUser.id == int(id))
        return db.session.scalar(query)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.anonymous_user = AnonymousUser

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template("error.html", error=exc), exc.code

    return app
