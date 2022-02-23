import datetime
import flask

UTC = datetime.timezone.utc

def now():
    return datetime.datetime.now(UTC)

def start():
    return flask.current_app.config.get('START_TIME')

def state():
    time = now()
    a    = start()
    z    = stop()

    if a and time < a:
        return 'before'
    if z and time > z:
        return 'after'
    return 'during'

def stop():
    return flask.current_app.config.get('END_TIME')
