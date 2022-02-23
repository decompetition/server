from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, EmailField, IntegerField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, ValidationError

from ...lib.models import Account


class NewUserForm(FlaskForm):
    name = StringField('Username',  validators = [
        InputRequired('Username is required.')
    ])

    password = PasswordField('Password', validators = [
        # Length(min=8, message='That\'s a crap password.'),
        InputRequired('Password is required.')
    ])

    disclaimer = BooleanField('I Agree',
        validators  = [InputRequired('You must accept the terms.')],
        description = (
            'This CTF is part of a research project on reverse engineering.  '
            'I agree that any data I provide may be recorded and used for '
            'statistical purposes. Personally identifying information '
            'will never be shared with anyone.'
        )
    )

    def validate_name(self, field):
        if Account.query.filter_by(name=field.data).first():
            raise ValidationError('This name is already taken.')


class AdminUserForm(FlaskForm):
    admin  = BooleanField('Admin')
    hidden = BooleanField('Hidden')
    banned = BooleanField('Banned')


class UserInfoForm(FlaskForm):
    security_involvement = SelectField('Security Involvement',
        description = 'What best describes your involvement in computer security?',
        validators  = [InputRequired()],
        choices     = [
            ('',             'Select...'),
            ('professional', 'Professional'),
            ('researcher',   'Researcher'),
            ('student',      'Student'),
            ('hobbyist',     'Hobbyist'),
            ('other',        'Other')
        ]
    )

    security_experience = IntegerField('Security Experience',
        description = 'How many years have you been involved in computer security?',
        validators  = [InputRequired(), NumberRange(min=0)],
        # widget      =  NumberInput(min=0)
    )

    reversing_experience = IntegerField('Reversing Experience',
        description = 'How many years have you been involved in reverse engineering?',
        validators  = [InputRequired(), NumberRange(min=0)],
        # widget      =  NumberInput(min=0)
    )

    reversing_workload = SelectField('Reversing Workload',
        description = 'How much of your paid time is spent reverse engineering?',
        validators  = [InputRequired()],
        choices     = [
            ('',     'Select...'),
            ('none', 'I\'m not paid to reverse anything.'),
            ('some', 'A little bit of my workload is reversing.'),
            ('half', 'Around half of my workload is reversing.'),
            ('most', 'Most or all of my workload is reversing.')
        ]
    )

    reversing_confidence = SelectField('Reversing Confidence',
        description = 'How much confidence do you have in your reversing skills?',
        validators  = [InputRequired()],
        choices     = [
            ('',     'Select...'),
            ('none', 'I have no idea what I\'m doing.'),
            ('some', 'I\'m still a beginner.'),
            ('half', 'I\'m an average reverser.'),
            ('lots', 'I\'m better than average.'),
            ('yuge', 'I am an expert.')
        ]
    )

    reversing_difficulty = SelectField('Reversing Difficulty',
        description = 'How difficult is completely recreating the source code of a small binary?',
        validators  = [InputRequired()],
        choices     = [
            ('',           'Select...'),
            ('trivial',    'Trivial'),
            ('easy',       'Easy'),
            ('moderate',   'Moderate'),
            ('difficult',  'Difficult'),
            ('impossible', 'Impossible')
        ]
    )

    codexp_c     = IntegerField('C',     validators=[NumberRange(min=1, max=5)])
    codexp_cpp   = IntegerField('C++',   validators=[NumberRange(min=1, max=5)])
    codexp_go    = IntegerField('Go',    validators=[NumberRange(min=1, max=5)])
    codexp_rust  = IntegerField('Rust',  validators=[NumberRange(min=1, max=5)])
    codexp_swift = IntegerField('Swift', validators=[NumberRange(min=1, max=5)])

    revexp_c     = IntegerField('C',     validators=[NumberRange(min=1, max=5)])
    revexp_cpp   = IntegerField('C++',   validators=[NumberRange(min=1, max=5)])
    revexp_go    = IntegerField('Go',    validators=[NumberRange(min=1, max=5)])
    revexp_rust  = IntegerField('Rust',  validators=[NumberRange(min=1, max=5)])
    revexp_swift = IntegerField('Swift', validators=[NumberRange(min=1, max=5)])

    tool_angr    = IntegerField('Angr',           validators=[NumberRange(min=1, max=3)])
    tool_binja   = IntegerField('Binary Ninja',   validators=[NumberRange(min=1, max=3)])
    tool_ghidra  = IntegerField('Ghidra',         validators=[NumberRange(min=1, max=3)])
    tool_ida     = IntegerField('Ida / Hex-Rays', validators=[NumberRange(min=1, max=3)])
    tool_cli     = IntegerField('objdump, etc.',  validators=[NumberRange(min=1, max=3)])
    tool_radare  = IntegerField('Radare',         validators=[NumberRange(min=1, max=3)])
    tool_tcpdump = IntegerField('tcpdump, etc.',  validators=[NumberRange(min=1, max=3)])
    tool_wshark  = IntegerField('Wireshark',      validators=[NumberRange(min=1, max=3)])
    tool_custom  = IntegerField('Custom Scripts', validators=[NumberRange(min=1, max=3)])

    tool_other = StringField('Other Tools',
        description='If we missed any reversing tools you frequently use, list them here.'
    )

    survey_email = EmailField('Email Address',
        validators  = [Optional()],
        description = (
            'If you\'re willing to take a brief follow-up survey '
            '(to help us improve for next year and for a chance to '
            'win a $50 gift card) leave your email address here.'
        )
    )


class UserFollowupForm(FlaskForm):
    reversing_confidence = SelectField('Reversing Confidence',
        description = 'How much confidence do you have in your reversing skills?',
        validators  = [InputRequired()],
        choices     = [
            ('',     'Select...'),
            ('none', 'I have no idea what I\'m doing.'),
            ('some', 'I\'m still a beginner.'),
            ('half', 'I\'m an average reverser.'),
            ('lots', 'I\'m better than average.'),
            ('yuge', 'I am an expert.')
        ]
    )

    reversing_difficulty = SelectField('Reversing Difficulty',
        description = 'How difficult is completely recreating the source code of a small binary?',
        validators  = [InputRequired()],
        choices     = [
            ('',           'Select...'),
            ('trivial',    'Trivial'),
            ('easy',       'Easy'),
            ('moderate',   'Moderate'),
            ('difficult',  'Difficult'),
            ('impossible', 'Impossible')
        ]
    )

    codexp_c     = IntegerField('C',     validators=[NumberRange(min=1, max=5)])
    codexp_cpp   = IntegerField('C++',   validators=[NumberRange(min=1, max=5)])
    codexp_go    = IntegerField('Go',    validators=[NumberRange(min=1, max=5)])
    codexp_rust  = IntegerField('Rust',  validators=[NumberRange(min=1, max=5)])
    codexp_swift = IntegerField('Swift', validators=[NumberRange(min=1, max=5)])

    revexp_c     = IntegerField('C',     validators=[NumberRange(min=1, max=5)])
    revexp_cpp   = IntegerField('C++',   validators=[NumberRange(min=1, max=5)])
    revexp_go    = IntegerField('Go',    validators=[NumberRange(min=1, max=5)])
    revexp_rust  = IntegerField('Rust',  validators=[NumberRange(min=1, max=5)])
    revexp_swift = IntegerField('Swift', validators=[NumberRange(min=1, max=5)])

    tool_deco    = IntegerField('This Web UI',    validators=[NumberRange(min=1, max=3)])
    tool_angr    = IntegerField('Angr',           validators=[NumberRange(min=1, max=3)])
    tool_binja   = IntegerField('Binary Ninja',   validators=[NumberRange(min=1, max=3)])
    tool_ghidra  = IntegerField('Ghidra',         validators=[NumberRange(min=1, max=3)])
    tool_ida     = IntegerField('Ida / Hex-Rays', validators=[NumberRange(min=1, max=3)])
    tool_cli     = IntegerField('objdump, etc.',  validators=[NumberRange(min=1, max=3)])
    tool_radare  = IntegerField('Radare',         validators=[NumberRange(min=1, max=3)])
    tool_tcpdump = IntegerField('tcpdump, etc.',  validators=[NumberRange(min=1, max=3)])
    tool_wshark  = IntegerField('Wireshark',      validators=[NumberRange(min=1, max=3)])
    tool_custom  = IntegerField('Custom Scripts', validators=[NumberRange(min=1, max=3)])

    tool_other   = StringField('Other Tools',
        description = 'If you liked to use tools we didn\'t list, add them here.'
    )

    deco_ux = SelectField('Interface Usability',
        description = 'What did you think of the web interface used to submit and diff code?',
        validators  = [InputRequired()],
        choices     = [
            ('',  'Select...'),
            ('1', 'It was terible.'),
            ('2', 'It wasn\'t very good.'),
            ('3', 'It was acceptable.'),
            ('4', 'It was pretty nice.'),
            ('5', 'It was wonderful.')
        ]
    )

    deco_speed = SelectField('Interface Reversing Speed',
        description = 'If you used the web interface to reverse, how did it affect your reversing speed?',
        validators  = [InputRequired()],
        choices     = [
            ('',  'Select...'),
            ('0', 'I didn\'t reverse in the web UI.'),
            ('1', 'I was much slower when using the web UI.'),
            ('2', 'I was somewhat slower when using the web UI.'),
            ('3', 'It didn\'t make much of a difference.'),
            ('4', 'I was somewhat faster when using the web UI.'),
            ('5', 'I was much faster when using the web UI.')
        ]
    )

    deco_code = SelectField('Interface Code Quality',
        description = 'If you used the web interface to reverse, how did it affect your code quality?',
        validators  = [InputRequired()],
        choices     = [
            ('',  'Select...'),
            ('0', 'I didn\'t reverse in the web UI.'),
            ('1', 'My code was much messier when using the web UI.'),
            ('2', 'My code was somewhat messier when using the web UI.'),
            ('3', 'It didn\'t make much of a difference.'),
            ('4', 'My code was somewhat cleaner when using the web UI.'),
            ('5', 'My code was much cleaner when using the web UI.')
        ]
    )

    comment_comp = TextAreaField('Competition Comments', description = (
        'If you have comments / questions / suggestions about '
        'the competition or the challenges, let us know!'
    ))

    comment_tool = TextAreaField('Tooling Comments', description = (
        'If you have anything to say about the disassembly, the web '
        'interface, or the website in general, say it here!'
    ))

    comment_misc = TextAreaField('Other Comments', description = (
        'Want to add something that\'s not covered above? Here\'s a text field!'
    ))

    survey_email = EmailField('Email Address',
        validators  = [Optional()],
        description = (
            'Enter your email address to be entered into our '
            '“Thank you for taking our surveys!” drawing. You\'ll '
            'have about a 15% chance to win a $50 Amazon gift card.'
        )
    )
