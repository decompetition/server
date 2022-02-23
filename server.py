#! /usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--init-db', action='store_true', help='initialize the database')
parser.add_argument('config', nargs='?', default='app/config/development.json', help='path to a config file')
args = parser.parse_args()

from app import create_app
app = create_app(args.config)

if __name__ == '__main__':
    if args.init_db:
        with app.app_context():
            app.db.create_all()
    else:
        app.run()
