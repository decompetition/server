from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Optional, ValidationError

import os

class LocalDirRequired:
    def __init__(self, message='Directory does not exist.'):
        self.message = message

    def __call__(self, form, field):
        if not os.path.isdir(field.data):
            raise ValidationError(self.message)

class LocalFileRequired:
    def __init__(self, message='File does not exist.'):
        self.message = message

    def __call__(self, form, field):
        if not os.path.isfile(field.data):
            raise ValidationError(self.message)

LANGUAGES = [
    ('c',     'C'),
    ('cpp',   'C++'),
    ('go',    'Go'),
    ('nim',   'Nim'),
    ('rust',  'Rust'),
    ('swift', 'Swift')
]

class ChallengeForm(FlaskForm):
    name = StringField('Name',  validators = [
        DataRequired()
    ])

    value = IntegerField('Value', validators = [
        DataRequired(),
        NumberRange(min=0)
    ])

    language = SelectField('Language', choices=LANGUAGES, validators = [
        DataRequired()
    ])

    functions = StringField('Functions', validators = [
        DataRequired()
    ])

    hidden = BooleanField('Hidden', default=False)

    container = StringField('Container', validators = [
        DataRequired()
    ])

    builder = StringField('Path to Build Script', validators = [
        DataRequired(),
        LocalFileRequired()
    ])

    tester = StringField('Path to Test Script', validators = [
        DataRequired(),
        LocalFileRequired()
    ])

    folder = StringField('Path to Challenge Folder', validators = [
        DataRequired(),
        LocalDirRequired()
    ])

    binary = StringField('Path to Binary', validators = [
        DataRequired(),
        LocalFileRequired()
    ])

    disasm = StringField('Path to Disassembly', validators = [
        Optional(),
        LocalFileRequired()
    ])

    decomp = StringField('Path to Starter Code', validators = [
        DataRequired(),
        LocalFileRequired()
    ])

    binja_url = StringField('Binary Ninja Cloud URL', validators = [
        Optional()
    ])

    @staticmethod
    def from_challenge_info(info):
        return ChallengeForm(
            name      = info.name,
            value     = info.value,
            language  = info.language,

            functions = ' '.join(info.functions),
            container = info.container,
            builder   = info.builder,
            tester    = info.tester,

            folder    = info.folder,
            # source    = info.source,
            decomp    = info.starter,
            binary    = info.binary,
            disasm    = info.disasm
        )


class ChallengeUploadForm(FlaskForm):
    config_path = StringField('Config File',
        description = 'Path to a config file on the app server.',
        validators  = [
            InputRequired(),
            LocalFileRequired()
        ]
    )
