import datetime
import flask
import flask_login
import os
import pytest

from app import create_app
from app.lib.models import Account, Challenge

USER_PASSWORDS = {}
TEAM_PASSWORDS = {}

def login(client, username):
    response = client.post('/login', data = {
        'password': USER_PASSWORDS[username],
        'username': username
    })
    assert response.status_code == 302
    assert flask_login.current_user.name == username

def team(name):
    return Account.query.filter_by(name=name, user=False).first()

def user(name):
    return Account.query.filter_by(name=name, user=True).first()

def seed(app):
    def add_team(name, password, email):
        team = Account(name=name, password=password, user=False)
        team.created_at = datetime.datetime.now()
        TEAM_PASSWORDS[name] = password
        app.db.session.add(team)
        return team

    def add_user(name, password, **kwargs):
        user = Account(name=name, password=password, user=True, **kwargs)
        user.created_at = datetime.datetime.now()
        USER_PASSWORDS[name] = password
        app.db.session.add(user)
        return user

    def add_challenge(name, value):
        challenge = Challenge(
            name      = name,
            value     = value,
            language  = 'c',
            functions = 'main foo',

            folder    = '/hi',
            binary    = '/hi/binary.out',
            disasm    = '/hi/disasm.yml',
            decomp    = '/hi/starter.c',

            container = 'decompetition/dummy',
            builder   = '/hi/build.sh',
            tester    = '/hi/tests.py',
        )

        app.db.session.add(challenge)
        return challenge

    with app.app_context():
        app.db.create_all()

        # No team
        add_user(name='admin', password='admin',   admin=True)
        add_user(name='god',   password='fiatlux', admin=True, hidden=True)
        add_user(name='Charles Pictet de Rochemont', password='SCHVIZZERLAND')

        gnomes = add_team(name='Gnomes', password='anklebiter', email='team@gnome.org')
        add_user(name='hungry', team=gnomes, password='nomnomnomnom')
        add_user(name='sneaky', team=gnomes, password='theyllneverknowwhatbitthem', hidden=True)
        add_user(name='stodgy', team=gnomes, password='bahhumbug')
        add_user(name='veruca', team=gnomes, password='dontlookinthesack')

        pirates = add_team(name='Pirates', password='yohoho', email='team@jolly.roger')
        add_user(name='hook',    team=pirates, password='ticktock')
        add_user(name='kidd',    team=pirates, password='goldbug')
        add_user(name='silver',  team=pirates, password='looongjohnny')
        add_user(name='sparrow', team=pirates, password='whyistherumalwaysgone')

        add_challenge('cinnamon',  100)
        add_challenge('tide-pods', 500)

        app.db.session.commit()

# This has to happen exactly once for... reasons:
path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test.json')
app  = create_app(path)
seed(app)

@pytest.fixture(scope='function')
def client():
    with app.app_context():
        app.db.session.begin(subtransactions=True)
        try:
            with app.test_client() as client:
                yield client
        finally:
            app.db.session.rollback()
