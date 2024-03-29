import json
import os

import structlog
from admin_views import LogAdminView, RolesAdminView, UserAdminView
from apis import api
from database import Log, Role, User, db, user_datastore
from flask import Flask, jsonify, render_template, request, url_for
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
api.init_app(app)
db.init_app(app)
mail.init_app(app)
admin.add_view(LogAdminView(Log, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RolesAdminView(Role, db.session))

migrate = Migrate(app, db)
logger.info("Ready loading admin views and api")


@app.route("/log")
@app.route("/log.json")
def log_request_info():
    body = request.get_data()
    headers = request.headers

    # formatted_headers = str(headers).replace(": ", ": \n").replace("; ", "; \n")
    headers_dict = {}
    for header in headers.to_list():
        headers_dict[header[0]] = header[1]

    formatted_headers = ""
    for header_name, header_value in headers_dict.items():
        value = header_value.replace(",", ", ")
        if header_name.upper() == "COOKIE":
            value = value.replace("_", "_\n")
        formatted_headers = "{}\n{}\n{}\n".format(
            formatted_headers, header_name.upper(), value
        )

    db_dict = {
        "headers": json.dumps(headers_dict),
        "ip": request.remote_addr,
        "http_connection": request.environ.get("HTTP_CONNECTION", ""),
        "http_cache_control": request.environ.get("HTTP_CACHE_CONTROL", ""),
        "http_cookie": request.environ.get("HTTP_COOKIE", ""),
        "http_user_agent": request.environ.get("HTTP_USER_AGENT", ""),
        "server_protocol": request.environ.get("SERVER_PROTOCOL", ""),
        "remote_port": request.environ.get("REMOTE_PORT", 0),
    }

    log = Log(**db_dict)
    db.session.add(log)

    # Handle JSON response
    if request.environ["PATH_INFO"] == "/log.json":
        db_dict["headers"] = headers_dict
        return jsonify(db_dict), 200

    # Handle HTML response
    return render_template(
        "index.html",
        body=body,
        headers=formatted_headers,
        ip=request.remote_addr,
        http_connection=db_dict["http_connection"],
        http_user_agent=db_dict["http_user_agent"],
        server_protocol=db_dict["server_protocol"],
        remote_port=db_dict["remote_port"],
        http_cache_control=db_dict["http_cache_control"],
    )


if __name__ == "__main__":
    app.run()
