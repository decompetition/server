import datetime
import functools

from flask import flash, redirect, request, session, url_for
from flask_login import current_user

from . import timing

def require(user=None, team=None, admin=None, running=None):
    def wrap(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            user_id = current_user.get_id()
            team_id = current_user.get_team_id()

            if user is True or team is not None or admin is not None:
                if not user_id:
                    flash('You need to log in to do that.', 'warning')
                    return redirect(url_for('login.login'))
            elif user is False:
                if user_id:
                    flash('You already have an account.', 'warning')
                    return redirect(url_for('users.show', id=user_id))

            if team is True:
                if not team_id:
                    flash('You need to join a team to do that.', 'warning')
                    return redirect(url_for('teams.join'))
            elif team is False:
                if team_id is not None and team_id != user_id:
                    flash('You already have a team.', 'warning')
                    return redirect(url_for('teams.show', id=team_id))

            if admin is True:
                if not current_user.is_admin():
                    flash('Only admins can do that.', 'warning')
                    return redirect(url_for('users.show', id=user_id))

            if running is True and not current_user.is_admin():
                state = timing.state()
                if state == 'before':
                    flash('The competition hasn\'t started yet.', 'warning')
                    return redirect(url_for('challenges.index'))
                # if state == 'after':
                #     flash('The competition is over.', 'warning')
                #     return redirect(url_for('challenges.index'))

            return callback(*args, **kwargs)
        return wrapper
    return wrap
