import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user

from ...lib.models  import db, Account, UserFollowup, UserInfo
from ...lib.require import require
from ...lib.scoring import user_solves
from ...lib.timing  import now

from .forms import NewUserForm, UserFollowupForm, UserInfoForm

blueprint = Blueprint('users', __name__)

@blueprint.route('/users', methods=['GET'])
def index():
    team  = db.aliased(Account)
    users = Account.query.filter_by(user=True)
    if not current_user.is_admin():
        users = users.filter_by(hidden=False, banned=False)
    users = users.join(Account.team.of_type(team), isouter=True).order_by(Account.name)
    return render_template('users/index.html', users=users.all())


@blueprint.route('/users/info', methods=['GET', 'POST'])
@require(user=True)
def info():
    if current_user.info_id is not None:
        flash('You already filled that out.')
        return redirect(url_for('challenges.index'))

    form = UserInfoForm()
    if form.validate_on_submit():
        current_user.info = UserInfo.from_form(form)
        db.session.add(current_user.info)
        db.session.add(current_user)
        db.session.commit()

        flash('Thank you for helping out!')
        return redirect(url_for('challenges.index'))

    return render_template('users/info.html', form=form)


# @blueprint.route('/users/followup', methods=['GET', 'POST'])
@require(user=True)
def followup():
    if current_user.followup_id is not None:
        flash('You already filled that out.')
        return redirect(url_for('challenges.index'))

    form = UserFollowupForm()
    if form.validate_on_submit():
        current_user.followup = UserFollowup.from_form(form)
        db.session.add(current_user.followup)
        db.session.add(current_user)
        db.session.commit()

        flash('Thanks for the feedback!')
        return redirect(url_for('challenges.index'))

    return render_template('users/followup.html', form=form)


@blueprint.route('/users/new', methods=['GET', 'POST'])
@require(user=False)
def new():
    form = NewUserForm()
    if form.validate_on_submit():
        user = Account.from_form(form, include=['password'], ignore=['disclaimer'])
        user.created_at = now()
        user.user = True
        if not Account.query.count():
            user.admin  = True
            user.hidden = True
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Welcome to the game!')
        # return redirect(url_for('challenges.index'))
        return redirect(url_for('users.info'))

    return render_template('users/new.html', form=form)


@blueprint.route('/users/<id>', methods=['GET'])
def show(id):
    user = Account.query.filter_by(id=id, user=True).first_or_404()
    return render_template('users/show.html', user=user, solves=user_solves(id))
