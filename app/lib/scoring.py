from sqlalchemy import desc
from .models import db, Account, Challenge, Submission

def scores(admin=False, end=None, challenge_id=None):
    maxquery = db.session.query(
        Submission.owner_id.label('account_id'),
        Submission.challenge_id.label('challenge_id'),
        db.func.max(Submission.score * Challenge.value).label('score')
    ).join(
        Submission.challenge
    ).group_by(
        'account_id',
        'challenge_id'
    )

    if end is not None:
        maxquery = maxquery.filter(Submission.created_at < end)
    if challenge_id is not None:
        maxquery = maxquery.filter(Submission.challenge_id == challenge_id)
    maxquery = maxquery.subquery()

    sumquery = db.session.query(
        maxquery.c.account_id.label('account_id'),
        db.func.sum(maxquery.c.score).label('score')
    ).group_by(
        'account_id'
    ).subquery()

    query = db.session.query(
        Account.id.label('id'),
        Account.name.label('name'),
        Account.user.label('is_user'),
        sumquery.c.score.label('score'),
        db.func.rank().over(
            order_by=desc('score')
        ).label('rank')
    ).join(
        sumquery, Account.id == sumquery.c.account_id,
    ).filter(
        Account.team_id == None,
        Account.hidden  == False
    ).order_by(
        desc('score')
    )

    # print(str(query))
    return query.all()


def solves(owner_id):
    return db.session.query(
        Challenge.id.label('id'),
        Challenge.name.label('name'),
        Challenge.value.label('possible'),
        Challenge.language.label('language'),
        db.func.max(Submission.created_at).label('created_at'),
        db.func.max(Submission.score).label('score')
    ).join(
        Submission.challenge
    ).filter(
        Submission.owner_id == owner_id
    ).group_by(
        Challenge.id
    ).order_by(
        desc('score'),
        desc('created_at')
    ).all()


def user_solves(user_id):
    query = db.session.query(
        Challenge.id.label('id'),
        Challenge.name.label('name'),
        Challenge.value.label('possible'),
        Challenge.language.label('language'),
        db.func.max(Submission.created_at).label('created_at'),
        db.func.max(Submission.score).label('score')
    ).join(
        Submission.challenge
    ).filter(
        Submission.user_id == user_id
    ).group_by(
        Challenge.id
    ).order_by(
        desc('score'),
        desc('created_at')
    )

    return query.all()


def firsts():
    minquery = db.session.query(
        db.func.min(Submission.id).label('submission_id')
    ).filter(
        Submission.score == 1.0
    ).group_by(
        Submission.challenge_id
    ).subquery()

    query = Submission.query.filter(
        Submission.id.in_(minquery)
    ).join(
        Submission.challenge,
        Submission.owner
    ).order_by(
        Submission.created_at
    )

    return query.all()
