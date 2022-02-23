from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user
from .forms import ChallengeForm, ChallengeUploadForm

from ...lib.challs  import ChallengeImpl
from ...lib.differ  import diff_all
from ...lib.models  import db, Account, Challenge, Submission
from ...lib.require import require
from ...lib.scoring import solves
from ...lib.timing  import now

import datetime
import json
import os
import yaml

def readfile(path):
    with open(path) as file:
        return file.read()

blueprint = Blueprint('challenges', __name__)

@blueprint.route('/challenges', methods=['GET'])
def index():
    begtime = current_app.config.get('START_TIME')
    if not current_user.is_admin() and begtime and begtime > now():
        challenges = []
        scoremap   = {}
    else:
        challenges = Challenge.query.order_by('name')
        if not current_user.is_admin():
            challenges = challenges.filter_by(hidden=False)
        challenges = challenges.all()
        scoremap   = {s.id:s.score for s in solves(current_user.get_owner_id())}
    return render_template('challenges/index.html', challenges=challenges, solves=scoremap)


@blueprint.route('/challenges/new', methods=['GET', 'POST'])
@require(admin=True)
def new():
    form = ChallengeForm()
    if form.validate_on_submit():
        challenge = Challenge.from_form(form)
        db.session.add(challenge)
        db.session.commit()
        flash('Challenge created.')
        return redirect(url_for('challenges.index'))
    return render_template('challenges/new.html', form=form)


@blueprint.route('/challenges/upload', methods=['GET', 'POST'])
@require(admin=True)
def upload():
    upload_form = ChallengeUploadForm()
    if upload_form.validate_on_submit():
        from ...lib.challs import load
        infos = load(upload_form.config_path.data)

        for info in infos:
            form = ChallengeForm.from_challenge_info(info)
            if not form.validate():
                db.session.rollback()
                return render_template('challenges/new.html', form=form)
            challenge = Challenge.from_form(form)
            db.session.add(challenge)
        db.session.commit()
        flash('Upload successful.')
        return redirect(url_for('challenges.index'))
    return render_template('challenges/upload.html', form=upload_form)


@blueprint.route('/challenges/<id>', methods=['GET'])
@require(user=True, running=True)
def show(id):
    challenge  = Challenge.query.get_or_404(id)
    submission = Submission.query.filter_by(
        user_id      = current_user.get_id(),
        challenge_id = challenge.id
    ).order_by(
        Submission.id.desc()
    ).first()

    if submission:
        decomp = submission.submission
        parent = submission.id
    else:
        decomp = readfile(challenge.decomp)
        parent = 0

    with open(challenge.disasm) as file:
        target = yaml.safe_load(file)

    return render_template('challenges/editor.html',
        challenge = challenge,
        target    = target,
        decomp    = decomp,
        parent    = parent
    )


@blueprint.route('/challenges/<id>', methods=['POST'])
@require(user=True, running=True)
def compile(id):
    # endtime = current_app.config.get('END_TIME')
    # if endtime and endtime <= now():
    #     return 'The competition has ended.', 403

    challenge  = Challenge.query.get_or_404(id)
    submission = Submission(
        challenge  = challenge,
        user_id    = current_user.get_id(),
        owner_id   = current_user.get_owner_id(),
        ip_address = request.remote_addr,
        submission = request.form['source'],
        parent_id  = request.form.get('parent'),
        created_at = now()
    )

    os.makedirs(submission.folder, exist_ok=True)
    with open(submission.source, 'w') as file:
        file.write(submission.submission)

    build = submission.compile()
    if build.returncode != 0:
        submission.test_score = 0.0
        submission.diff_score = 0.0
        submission.diff_bonus = 0.0
        submission.score      = 0.0
        if not current_user.is_admin():
            db.session.add(submission)
            db.session.commit()

        return json.dumps({
            'id':     submission.id,
            'stdout': build.stdout
        })

    disasm = submission.disassemble()
    with open(challenge.disasm) as file:
        target = yaml.safe_load(file)
    hunks, delta = diff_all(disasm, target)
    tests = submission.test()

    submission.test_score = tests['pass'] / tests['total']
    submission.diff_score = delta[1]      / delta[3]
    submission.diff_bonus = 1.0 if submission.diff_score == 1.0 else 0.0
    submission.score      = sum([
        0.2 * submission.test_score,
        0.6 * submission.diff_score,
        0.2 * submission.diff_bonus
    ])

    if not current_user.is_admin():
        db.session.add(submission)
        db.session.commit()

    return json.dumps({
        'id':        submission.id,
        'stdout':    build.stdout,
        'functions': hunks,
        'scores':    {
            'ins':   delta[0],
            'del':   delta[2],
            'tests': submission.test_score,
            'diffs': submission.diff_score,
            'bonus': submission.diff_bonus,
            'total': submission.score
        }
    })


@blueprint.route('/challenges/<id>/download', methods=['GET'])
@require(user=True)
def download(id):
    begtime = current_app.config.get('START_TIME')
    if begtime and begtime > now():
        flash('The competition hasn\'t started yet.', 'warning')
        return redirect(url_for('challenges.index'))

    challenge = Challenge.query.get_or_404(id)
    return send_file(challenge.binary,
        mimetype      = 'application/octet-stream',
        download_name = challenge.name,
        as_attachment = True
    )


@blueprint.route('/challenges/<id>/edit', methods=['GET', 'POST'])
@require(admin=True)
def edit(id):
    challenge = Challenge.query.get_or_404(id)
    form = ChallengeForm(obj=challenge)
    if form.validate_on_submit():
        challenge.set_attributes(form)
        db.session.add(challenge)
        db.session.commit()

        flash('Challenge updated.')
        return redirect(url_for('challenges.index'))
    return render_template('challenges/edit.html', challenge=challenge, form=form)


@blueprint.route('/challenges/<id>', methods=['DELETE'])
@require(admin=True)
def delete(id):
    challenge = Challenge.filter_by(id=id).delete()
    flash('Challenge deleted.')
    return redirect(url_for('challenges.index'))

@blueprint.route('/challenges/<id>/submissions.json', methods=['GET'])
@require(user=True, running=True)
def submissions(id):
    subquery = db.session.query(
        db.func.max(Submission.id).label('submission_id'),
        Submission.user_id.label('user_id')
    ).select_from(
        Submission
    ).filter(
        Submission.challenge_id == id,
        Submission.owner_id     == current_user.get_owner_id()
    ).group_by(
        Submission.user_id
    ).subquery()

    query = db.session.query(
        Submission.id.label('id'),
        Account.name.label('author'),
        Submission.score.label('score')
    ).select_from(
        subquery
    ).join(
        Account, Account.id == subquery.c.user_id
    ).join(
        Submission, Submission.id == subquery.c.submission_id
    )

    result = [{'id': 0, 'author': 'Starter Code', 'score': 0}]
    for row in query.all():
        result.append({
            'id':     row.id,
            'author': row.author,
            'score':  row.score
        })

    return json.dumps(result)

@blueprint.route('/challenges/<cid>/submissions/<sid>.json', methods=['GET'])
@require(user=True, running=True)
def submission(cid, sid):
    if str(sid) == '0':
        challenge = Challenge.query.get_or_404(cid)
        return json.dumps({
            'id':     0,
            'source': readfile(challenge.decomp)
        })

    submission = Submission.query.filter_by(
        owner_id     = current_user.get_owner_id(),
        challenge_id = cid,
        id           = sid
    ).first_or_404()

    return json.dumps({
        'id':     sid,
        'source': submission.submission
    })
