from flask import current_app
from flask_security.forms import ConfirmRegisterForm, RegisterForm
from werkzeug.local import LocalProxy
from wtforms import StringField
from wtforms.validators import DataRequired

_security = LocalProxy(lambda: current_app.extensions["security"])


class ExtraUserFields:
    username = StringField("Username", [DataRequired()])
    first_name = StringField("First Name", [DataRequired()])
    last_name = StringField("Last Name", [DataRequired()])


class ExtendedRegisterForm(RegisterForm, ExtraUserFields):
    pass


class ExtendedJSONRegisterForm(ConfirmRegisterForm, ExtraUserFields):
    pass
