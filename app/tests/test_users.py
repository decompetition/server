from flask import url_for
from flask_login import current_user

from .fixtures import client, login
from app.lib.models import Account

def test_user_index(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert b'<h1>Users</h1>' in response.data

def test_user_index_hides_hidden_users(client):
    login(client, 'sparrow')
    response = client.get('/users')
    assert response.status_code == 200
    assert b'sparrow'    in response.data
    assert b'sneaky' not in response.data
    assert b'god'    not in response.data

def test_user_index_shows_hidden_users_to_admin(client):
    login(client, 'admin')
    response = client.get('/users')
    assert response.status_code == 200
    assert b'sparrow' in response.data
    assert b'sneaky'  in response.data
    assert b'god'     in response.data


def test_new_user(client):
    response = client.get('/users/new')
    assert response.status_code == 200
    assert b'<h1>New User</h1>' in response.data

def test_new_user_redirect(client):
    login(client, 'sparrow')
    response = client.get('/users/new')
    assert response.status_code == 302

def test_new_user_redirect_for_admin(client):
    login(client, 'admin')
    response = client.get('/users/new')
    assert response.status_code == 302


def test_username_required(client):
    response = client.post('/users/new', data = {
        'password': 'hullabaloo'
    }, follow_redirects=True)
    assert b'Username is required.' in response.data
    assert current_user.get_id() is None

def test_password_required(client):
    response = client.post('/users/new', data = {
        'username': 'joe'
    }, follow_redirects=True)
    assert b'Password is required.' in response.data
    assert current_user.get_id() is None

def test_username_unique(client):
    response = client.post('/users/new', data = {
        'name':     'sparrow',
        'password': 'imabird'
    }, follow_redirects=True)
    assert b'This name is already taken.' in response.data
    assert current_user.get_id() is None


def test_create_user(client):
    response = client.post('/users/new', data = {
        'name':      'bob',
        'password':  'bob',
        'disclaimer': True
    }, follow_redirects=True)
    assert current_user.get_id() is not None
    assert current_user.name == 'bob'

    assert current_user.admin   is False
    assert current_user.hidden  is False
    assert current_user.banned  is False

def test_create_first_user(client):
    Account.query.delete()
    response = client.post('/users/new', data = {
        'name':      'adam',
        'password':  'madamimadam',
        'disclaimer': True
    }, follow_redirects=True)
    assert current_user.get_id() is not None
    assert current_user.name == 'adam'

    assert current_user.admin   is True
    assert current_user.hidden  is True
    assert current_user.banned  is False

def test_create_user_redirect(client):
    response = client.post('/users/new', data = {
        'name':      'jon',
        'password':  'iknownothing',
        'disclaimer': True
    }, follow_redirects=True)
    assert current_user.name == 'jon'
    assert current_user.get_id() is not None
    assert b'<h1>User Info</h1>' in response.data
