import datetime

from flask import request, url_for
from flask_login import current_user
from .fixtures import app, client, login, user


from app.lib.models import Submission

def add_submission(username, challenge_id, score):
    submission = Submission(
        user_id      = user(username).get_id(),
        owner_id     = user(username).get_owner_id(),
        challenge_id = challenge_id,
        ip_address   = '127.0.0.1',
        created_at   = datetime.datetime.now(),
        submission   = 'print("Hello, world!")',
        diff_score   = 0,
        test_score   = 0,
        score        = score
    )

    app.db.session.add(submission)
    # app.db.session.commit()
    return submission

def test_score_simple(client):
    add_submission('sparrow', 1, 0.5)
    assert Submission.query.count() == 1

    response = client.get('/scoreboard')
    print(response.data)

    assert response.status_code == 200
    assert b'Pirates' in response.data

def test_score_many_submissions(client):
    add_submission('sparrow', 1, 0.2)
    add_submission('sparrow', 1, 0.5)
    add_submission('silver',  1, 0.4)
    add_submission('kidd',    1, 0.9)
    add_submission('sparrow', 1, 0.7)
    assert Submission.query.count() == 5

    response = client.get('/scoreboard')
    assert response.status_code == 200
    assert b'Pirates' in response.data
    assert b'90.00'   in response.data

def test_score_many_challenges(client):
    add_submission('sparrow', 1, 0.1)
    add_submission('sparrow', 2, 0.8)
    add_submission('silver',  1, 0.3)
    add_submission('kidd',    2, 0.2)
    add_submission('sparrow', 1, 0.6)
    add_submission('sparrow', 1, 0.9)
    assert Submission.query.count() == 6

    response = client.get('/scoreboard')
    assert response.status_code == 200
    assert b'Pirates' in response.data
    assert b'490.00'  in response.data
