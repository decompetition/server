import datetime
import json

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ...lib.models  import db, Account
from ...lib.require import require
from ...lib.scoring import solves
from ...lib.timing  import now

from .forms import TeamForm, TeamJoinForm, TeamLeaveForm

blueprint = Blueprint('teams', __name__)

@blueprint.route('/teams', methods=['GET'])
def index():
    teams = Account.query.filter_by(user=False).order_by(Account.name).all()
    return render_template('teams/index.html', teams=teams)


@blueprint.route('/teams/new', methods=['GET', 'POST'])
@require(team=False)
def new():
    form = TeamForm()
    if form.validate_on_submit():
        team = Account.from_form(form, include=['password'])
        team.created_at = now()
        team.user = False
        current_user.team = team
        db.session.add(current_user)
        db.session.add(team)
        db.session.commit()

        flash('Team created.')
        return redirect(url_for('teams.show', id=team.id))

    return render_template('teams/new.html', form=form)


@blueprint.route('/teams/join', methods=['GET', 'POST'])
@require(team=False)
def join():
    form = TeamJoinForm()
    if form.validate_on_submit():
        current_user.team_id = form.team.id
        current_user.captain = False
        db.session.add(current_user)
        db.session.commit()

        flash('Welcome to the team!')
        return redirect(url_for('teams.show', id=current_user.team_id))

    teams = Account.query.filter_by(user=False).order_by('name').all()
    if not teams:
        flash('No teams exist yet, but you can create one.')
        return redirect(url_for('teams.new'))

    form.team_id.choices = [(t.id, t.name) for t in teams]
    return render_template('teams/join.html', form=form)


@blueprint.route('/teams/leave', methods=['GET', 'POST'])
@require(team=True)
def leave():
    form = TeamLeaveForm()
    if form.validate_on_submit():
        current_user.team_id = None
        db.session.add(current_user)
        db.session.commit()

        flash('You have left the team.')
        return redirect(url_for('users.show', id=current_user.id))

    team = current_user.team
    return render_template('teams/leave.html', team=team, form=form)


@blueprint.route('/teams/<id>', methods=['GET'])
def show(id):
    team = Account.query.filter_by(id=id, user=False).first_or_404()
    return render_template('teams/show.html', team=team, solves=solves(id))
