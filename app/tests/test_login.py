from flask_login import current_user

from .fixtures import client

def test_get_root_page(client):
    response = client.get('/')
    assert b'<h1>Decompetition' in response.data

def test_get_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<h1>Log In</h1>' in response.data

def test_no_such_user(client):
    response = client.post('/login', data = {
        'username': 'yorick',
        'password': 'alas'
    })
    assert b'No such user.' in response.data

def test_incorrect_password(client):
    response = client.post('/login', data = {
        'username': 'sparrow',
        'password': 'nopenopenope'
    })
    assert b'Incorrect password.' in response.data

def test_successful_login(client):
    response = client.post('/login', data = {
        'username': 'Charles Pictet de Rochemont',
        'password': 'SCHVIZZERLAND'
    })
    assert current_user.name == 'Charles Pictet de Rochemont'

def test_redirect_to_join_page(client):
    response = client.post('/login', data = {
        'username': 'Charles Pictet de Rochemont',
        'password': 'SCHVIZZERLAND'
    }, follow_redirects=True)
    assert current_user.get_team_id() is None
    assert b'<h1>User Info</h1>' in response.data

# def test_redirect_to_challenges_page(client):
#     response = client.post('/login', data = {
#         'username': 'sparrow',
#         'password': 'whyistherumalwaysgone'
#     }, follow_redirects=True)
#     assert current_user.get_team_id() is not None
#     assert b'<h1>Challenges</h1>' in response.data


def test_logout(client):
    response = client.post('/login', data = {
        'username': 'sparrow',
        'password': 'whyistherumalwaysgone'
    })
    assert current_user.get_id() is not None

    response = client.get('/')
    assert current_user.get_id() is not None

    response = client.post('/logout')
    assert current_user.get_id() is None

def test_logout_redirect(client):
    response = client.post('/logout', follow_redirects=True)
    assert b'<h1>Log In</h1>' in response.data
