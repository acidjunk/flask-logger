from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_security import utils
from wtforms import PasswordField


class AuthModelMixin(ModelView):
    def is_accessible(self):
        # Prevent administration of Model unless the currently logged-in user has the "admin" role
        if not current_user:
            return False
        try:
            if "Admin" in current_user.roles:
                return True
        except AttributeError:
            return False


class UserAdminView(AuthModelMixin):
    column_display_pk = True
    # Don't display the password on the list of Users
    column_exclude_list = list = ("password",)
    column_default_sort = ("created_at", True)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ("password",)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    can_set_page_size = True

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdminView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField("New Password")
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.hash_password(model.password2)


class RolesAdminView(AuthModelMixin):
    column_display_pk = True


class BaseAdminView(AuthModelMixin):
    can_set_page_size = True


class LogAdminView(AuthModelMixin):
    column_display_pk = True
    column_list = [
        "id",
        "headers",
        "body",
        "created_at",
    ]
    # Don't display the password on the list of Users

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_default_sort = ("created_at", True)
    column_auto_select_related = True
    can_set_page_size = True
    can_view_details = True
    can_edit = False
    can_delete = True
    can_create = False

