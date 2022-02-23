from flask import request, url_for
from flask_login import current_user
from .fixtures import client, login, team

# from app.lib.models import Team

def test_team_index(client):
    response = client.get('/teams')
    assert response.status_code == 200
    assert b'<h1>Teams</h1>' in response.data
    assert b'Gnomes'         in response.data
    assert b'Pirates'        in response.data


def test_new_team_requires_login(client):
    response = client.get('/teams/new', follow_redirects=True)
    assert request.path == url_for('login.login')

def test_new_team_requires_no_team(client):
    login(client, 'kidd')
    response = client.get('/teams/new', follow_redirects=True)
    assert b'You already have a team.' in response.data

def test_new_team(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.get('/teams/new')
    assert response.status_code == 200
    assert b'<h1>New Team</h1>' in response.data


def test_create_team(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.post('/teams/new', data = {
        'name':     'Switzerland',
        'password': '5wi723r14nd'
    }, follow_redirects=True)
    assert b'<h1>Switzerland</h1>' in response.data

    assert current_user.name == 'Charles Pictet de Rochemont'
    assert current_user.team.name == 'Switzerland'
    # assert current_user.captain == True

def test_create_team_requires_no_team(client):
    login(client, 'veruca')
    response = client.post('/teams/new', data = {
        'name':     'The Bad Nuts',
        'password': 'honeyroasted'
    }, follow_redirects=True)
    assert b'You already have a team.' in response.data
    assert current_user.team.name == 'Gnomes'


def test_join_team_page_requires_login(client):
    response = client.get('/teams/join', follow_redirects=True)
    assert request.path == url_for('login.login')

def test_join_team_page_requires_no_team(client):
    login(client, 'silver')
    response = client.get('/teams/join', follow_redirects=True)
    assert b'You already have a team.' in response.data

def test_join_team_page(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.get('/teams/join')
    assert response.status_code == 200
    assert b'<h1>Join Team</h1>' in response.data


def test_join_team_requires_login(client):
    response = client.post('/teams/join', data = {
        'team_id':  team('Pirates').id,
        'password': 'yohoho'
    }, follow_redirects=True)
    assert request.path == url_for('login.login')

def test_join_team_requires_no_team(client):
    login(client, 'hungry')
    response = client.post('/teams/join', data = {
        'team_id':  team('Pirates').id,
        'password': 'yohoho'
    }, follow_redirects=True)
    assert b'You already have a team.' in response.data

def test_join_team_requires_existing_team(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.post('/teams/join', data = {
        'team_id':  -42,
        'password': 'dontcare'
    }, follow_redirects=True)
    assert b'No such team.' in response.data

def test_join_team_requires_team_password(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.post('/teams/join', data = {
        'team_id':  team('Pirates').id,
        'password': 'ARRRRRR'
    }, follow_redirects=True)
    assert b'Incorrect password.' in response.data

def test_join_team(client):
    login(client, 'Charles Pictet de Rochemont')
    response = client.post('/teams/join', data = {
        'team_id':  team('Pirates').id,
        'password': 'yohoho'
    }, follow_redirects=True)
    assert b'Welcome to the team!' in response.data

    assert current_user.name == 'Charles Pictet de Rochemont'
    assert current_user.team.name == 'Pirates'
    # assert current_user.captain == False



