from flask import Blueprint, flash, redirect, render_template, url_for
import flask_login

from .forms import LoginForm

blueprint = Blueprint('login', __name__)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flask_login.login_user(form.user)
        if not form.user.info_id:
            return redirect(url_for('users.info'))
        return redirect(url_for('challenges.index'))
    return render_template('login/login.html', form=form)


@blueprint.route('/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login.login'))
