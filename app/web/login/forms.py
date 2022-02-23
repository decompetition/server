from flask_wtf import FlaskForm
from functools import cached_property
from wtforms import PasswordField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from ...lib.models import Account

class LoginForm(FlaskForm):
    username = StringField('Username',  validators = [
        InputRequired()
    ])

    password = PasswordField('Password', validators = [
        InputRequired()
    ])

    @cached_property
    def user(self):
      return Account.query.filter_by(name=self.username.data, user=True).first()

    def validate_username(self, field):
        if not self.user:
            raise ValidationError('No such user.')

    def validate_password(self, field):
        if self.user and not self.user.check_password(field.data):
            raise ValidationError('Incorrect password.')
