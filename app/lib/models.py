import flask_sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os

from . import challs
from . import minidis
from . import sandbox

db = flask_sqlalchemy.SQLAlchemy()

class ModelMixin:
    @classmethod
    def from_form(Model, form, **kwargs):
        model = Model()
        model.set_attributes(form, **kwargs)
        return model

    def set_attributes(self, form, include=[], ignore=[]):
        for field in form:
            if field.name == 'csrf_token':
                continue
            if not hasattr(self, field.name):
                if field.name in ignore:
                    continue
                if field.name not in include:
                    raise Exception('No such attribute: ' + field.name)
            setattr(self, field.name, field.data)


class Account(ModelMixin, db.Model):
    __tablename__ = 'accounts'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String( 80), nullable=False, unique=True)
    hash        = db.Column(db.String(120), nullable=False)
    team_id     = db.Column(db.Integer, db.ForeignKey('accounts.id',  ondelete='SET NULL'))
    info_id     = db.Column(db.Integer, db.ForeignKey('infos.id',     ondelete='SET NULL'))
    followup_id = db.Column(db.Integer, db.ForeignKey('followups.id', ondelete='SET NULL'))


    user        = db.Column(db.Boolean,  nullable=False)
    admin       = db.Column(db.Boolean,  nullable=False, default=False)
    hidden      = db.Column(db.Boolean,  nullable=False, default=False)
    banned      = db.Column(db.Boolean,  nullable=False, default=False)
    created_at  = db.Column(db.DateTime, nullable=False)

    team = db.relationship('Account', backref=db.backref('members', lazy=True), foreign_keys=team_id, remote_side=id)

    def check_password(self, password):
        return check_password_hash(self.hash, password)

    def get_id(self):
        return self.id

    def get_owner_id(self):
        if self.user is False or self.team_id is None:
            return self.id
        return self.team_id

    def get_team_id(self):
        return self.team_id

    def is_active(self):
        return not self.banned

    def is_admin(self):
        return self.admin

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.id is not None

    def set_password(self, password):
        self.hash = generate_password_hash(password, method='sha384')

    def __repr__(self):
        return '<%s %d: %s>' % (('User' if self.user else 'Team'), self.id, self.name)

    password = property(None, set_password)


class Challenge(ModelMixin, db.Model):
    __tablename__ = 'challenges'

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String( 80), nullable=False)
    value     = db.Column(db.Integer,     nullable=False)

    functions = db.Column(db.String(999), nullable=False)
    language  = db.Column(db.String(120), nullable=False)

    container = db.Column(db.String(120), nullable=False)
    builder   = db.Column(db.String(120), nullable=False)
    tester    = db.Column(db.String(120), nullable=False)

    folder    = db.Column(db.String(120), nullable=False)
    binary    = db.Column(db.String(120), nullable=False)
    disasm    = db.Column(db.String(120), nullable=False)
    decomp    = db.Column(db.String(120), nullable=False)

    hidden    = db.Column(db.Boolean, nullable=False, default=True)
    binja_url = db.Column(db.String(120))

    @property
    def extension(self):
        return challs.LANGUAGES[self.language].extension


class Submission(ModelMixin, db.Model):
    __tablename__ = 'submissions'

    id           = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey(  'accounts.id', ondelete='CASCADE'), nullable=False)
    owner_id     = db.Column(db.Integer, db.ForeignKey(  'accounts.id', ondelete='CASCADE'), nullable=False)
    parent_id    = db.Column(db.Integer)

    ip_address   = db.Column(db.String(80), nullable=False)
    created_at   = db.Column(db.DateTime,   nullable=False)

    submission   = db.Column(db.Text,       nullable=False)
    score        = db.Column(db.Float,      nullable=False)
    test_score   = db.Column(db.Float,      nullable=False)
    diff_score   = db.Column(db.Float,      nullable=False)

    @property
    def binary(self):
        return os.path.join(self.folder, 'binary.out')

    def compile(self):
        return sandbox.build(self.challenge, self)

    def disassemble(self):
        chal = self.challenge
        return minidis.disassemble(self.binary, chal.language, chal.functions.split())

    @property
    def folder(self):
        # NOTE: This will cause race conditions if people share a user account:
        return os.path.join('/tmp/decompetition', str(self.user_id))

    @property
    def source(self):
        return os.path.join(self.folder, 'source' + self.challenge.extension)

    def test(self):
        return sandbox.test(self.challenge, self)

    challenge    = db.relationship('Challenge', backref=db.backref('submissions', lazy=True))
    user         = db.relationship('Account',                                                 foreign_keys=user_id)
    owner        = db.relationship('Account',   backref=db.backref('submissions', lazy=True), foreign_keys=owner_id)


class UserInfo(ModelMixin, db.Model):
    __tablename__ = 'infos'

    id                   = db.Column(db.Integer, primary_key=True)
    security_involvement = db.Column(db.String(20))
    security_experience  = db.Column(db.Integer)
    reversing_experience = db.Column(db.Integer)
    reversing_workload   = db.Column(db.String(20))
    reversing_confidence = db.Column(db.String(20))
    reversing_difficulty = db.Column(db.String(20))
    survey_email         = db.Column(db.String(80))

    codexp_c     = db.Column(db.Integer)
    codexp_cpp   = db.Column(db.Integer)
    codexp_go    = db.Column(db.Integer)
    codexp_rust  = db.Column(db.Integer)
    codexp_swift = db.Column(db.Integer)

    revexp_c     = db.Column(db.Integer)
    revexp_cpp   = db.Column(db.Integer)
    revexp_go    = db.Column(db.Integer)
    revexp_rust  = db.Column(db.Integer)
    revexp_swift = db.Column(db.Integer)

    tool_angr    = db.Column(db.Integer)
    tool_binja   = db.Column(db.Integer)
    tool_ghidra  = db.Column(db.Integer)
    tool_ida     = db.Column(db.Integer)
    tool_cli     = db.Column(db.Integer)
    tool_radare  = db.Column(db.Integer)
    tool_tcpdump = db.Column(db.Integer)
    tool_wshark  = db.Column(db.Integer)
    tool_custom  = db.Column(db.Integer)
    tool_other   = db.Column(db.String(120))

    user = db.relationship('Account', backref=db.backref('info', lazy=True))

class UserFollowup(ModelMixin, db.Model):
    __tablename__ = 'followups'

    id                   = db.Column(db.Integer, primary_key=True)
    reversing_confidence = db.Column(db.String(20))
    reversing_difficulty = db.Column(db.String(20))
    survey_email         = db.Column(db.String(80))

    codexp_c     = db.Column(db.Integer)
    codexp_cpp   = db.Column(db.Integer)
    codexp_go    = db.Column(db.Integer)
    codexp_rust  = db.Column(db.Integer)
    codexp_swift = db.Column(db.Integer)

    revexp_c     = db.Column(db.Integer)
    revexp_cpp   = db.Column(db.Integer)
    revexp_go    = db.Column(db.Integer)
    revexp_rust  = db.Column(db.Integer)
    revexp_swift = db.Column(db.Integer)

    tool_deco    = db.Column(db.Integer)
    tool_angr    = db.Column(db.Integer)
    tool_binja   = db.Column(db.Integer)
    tool_ghidra  = db.Column(db.Integer)
    tool_ida     = db.Column(db.Integer)
    tool_cli     = db.Column(db.Integer)
    tool_radare  = db.Column(db.Integer)
    tool_tcpdump = db.Column(db.Integer)
    tool_wshark  = db.Column(db.Integer)
    tool_custom  = db.Column(db.Integer)
    tool_other   = db.Column(db.String(120))

    comment_tool = db.Column(db.Text)
    comment_comp = db.Column(db.Text)
    comment_misc = db.Column(db.Text)

    user = db.relationship('Account', backref=db.backref('followup', lazy=True))
