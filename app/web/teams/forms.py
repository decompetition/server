from flask_wtf import FlaskForm
from functools import cached_property
from wtforms import PasswordField, SelectField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from ...lib.models import Account

class TeamForm(FlaskForm):
    name = StringField('Team Name',
        description = 'All user and team names must be unique.',
        validators  = [InputRequired()]
    )

    password = PasswordField('Team Password',
        description = 'Anyone who knows this password will be able to join the team.',
        validators  = [InputRequired()]
    )

    # email = StringField('Email Address',
    #     widget      =  EmailInput(),
    #     validators  = [InputRequired()],
    #     description = (
    #         'This will be used during the competition (if '
    #         'necessary) and to send out final results.'
    #     )
    # )

    def validate_name(self, field):
        if Account.query.filter_by(name=field.data).first():
            raise ValidationError('This name is already taken.')


class TeamJoinForm(FlaskForm):
    team_id = SelectField('Team', choices=[], coerce=int, validators = [
        InputRequired()
    ], validate_choice=False)

    password = PasswordField('Password', validators = [
        InputRequired()
    ])

    @cached_property
    def team(self):
        return Account.query.filter_by(id=self.team_id.data, user=False).first()

    def validate_team_id(self, field):
        if not self.team:
            raise ValidationError('No such team.')

    def validate_password(self, field):
        if self.team and not self.team.check_password(field.data):
            raise ValidationError('Incorrect password.')


class TeamLeaveForm(FlaskForm):
    pass
