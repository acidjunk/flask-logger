import os

import structlog
from admin_views import BaseAdminView, RolesAdminView, UserAdminView
from database import Log, Role, User, db, user_datastore
from flask import Flask, request, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import Security
from security import ExtendedJSONRegisterForm, ExtendedRegisterForm

logger = structlog.get_logger(__name__)

# Create app
app = Flask(__name__, static_url_path="/static")
app.url_map.strict_slashes = False
# NOTE: the extra headers need to be available in the API gateway: that is handled by zappa_settings.json
CORS(
    app,
    supports_credentials=True,
    resources="/*",
    allow_headers="*",
    origins="*",
    expose_headers="Authorization,Content-Type,Authentication-Token,Content-Range",
)
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:@localhost/logger-test"
)  # setup Travis

app.config["DEBUG"] = False if not os.getenv("DEBUG") else True
app.config["SECRET_KEY"] = (
    os.getenv("SECRET_KEY") if os.getenv("SECRET_KEY") else "super-secret"
)
admin = Admin(app, name="Logger", template_mode="bootstrap3")

app.config["FLASK_ADMIN_SWATCH"] = "flatly"
app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
app.config["SECRET_KEY"] = (
    os.getenv("SECRET_KEY") if os.getenv("SECRET_KEY") else "super-secret"
)
app.config["SECURITY_PASSWORD_HASH"] = "pbkdf2_sha256"
app.config["SECURITY_PASSWORD_SALT"] = (
    os.getenv("SECURITY_PASSWORD_SALT")
    if os.getenv("SECURITY_PASSWORD_SALT")
    else "SALTSALTSALT"
)
# More Flask Security settings
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_CONFIRMABLE"] = True
app.config["SECURITY_RECOVERABLE"] = True
app.config["SECURITY_CHANGEABLE"] = True
app.config["SECURITY_USER_IDENTITY_ATTRIBUTES"] = ["email"]

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Replace the next six lines with your own SMTP server settings
app.config["SECURITY_EMAIL_SENDER"] = (
    os.getenv("SECURITY_EMAIL_SENDER")
    if os.getenv("SECURITY_EMAIL_SENDER")
    else "no-reply@example.com"
)
app.config["MAIL_SERVER"] = (
    os.getenv("MAIL_SERVER") if os.getenv("MAIL_SERVER") else "smtp.gmail.com"
)
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = (
    os.getenv("MAIL_USERNAME") if os.getenv("MAIL_USERNAME") else "no-reply@example.com"
)
app.config["MAIL_PASSWORD"] = (
    os.getenv("MAIL_PASSWORD") if os.getenv("MAIL_PASSWORD") else "somepassword"
)

# Todo: check if we can fix this without completely disabling it: it's only needed when login request is not via .json
app.config["WTF_CSRF_ENABLED"] = False

# Setup Flask-Security with extended user registration
security = Security(
    app,
    user_datastore,
    register_form=ExtendedRegisterForm,
    confirm_register_form=ExtendedJSONRegisterForm,
)
login_manager = LoginManager(app)
mail = Mail()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Views
db.init_app(app)
mail.init_app(app)
admin.add_view(BaseAdminView(Log, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RolesAdminView(Role, db.session))

migrate = Migrate(app, db)
logger.info("Ready loading admin views and api")


@app.route("/log")
def log_request_info():
    logger.debug("Headers: %s", request.headers)
    logger.debug("Body: %s", request.get_data())


if __name__ == "__main__":
    app.run()
