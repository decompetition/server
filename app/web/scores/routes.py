from flask import Blueprint, current_app, jsonify, render_template, request
import datetime

from ...lib.models  import Challenge
from ...lib.scoring import firsts, scores
from ...lib.timing  import now

blueprint = Blueprint('scores', __name__)


@blueprint.route('/scoreboard', methods=['GET'])
def html():
    endtime = current_app.config.get('END_TIME')
    if endtime and endtime <= now():
        official = (request.args.get('scores') == 'official')
        if not official: endtime = None
    else:
        official = None

    teams = scores(end=endtime)
    return render_template('scores/scoreboard.html', teams=teams, official=official)


@blueprint.route('/firstblood', methods=['GET'])
def firstblood():
    return render_template('scores/firstblood.html', submissions=firsts())


@blueprint.route('/scoreboard.json', methods=['GET'])
def json():
    endtime   = current_app.config.get('END_TIME')
    standings = []

    for team in scores(end=endtime):
        standings.append({
            'team':  team.name,
            'score': round(team.score, 2),
            'pos':   team.rank
        })

    return jsonify({'standings': standings})


@blueprint.route('/challenges/<id>/leaderboard', methods=['GET'])
def challenge(id):
    challenge = Challenge.query.get_or_404(id)
    endtime   = current_app.config.get('END_TIME')
    if endtime and endtime <= now():
        official = (request.args.get('scores') == 'official')
        if not official: endtime = None
    else:
        official = None

    teams = scores(end=endtime, challenge_id=id)
    return render_template('scores/challenge.html', teams=teams, official=official, challenge=challenge)
