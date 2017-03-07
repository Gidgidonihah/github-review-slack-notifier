""" Flask app for github hook server. """
import os

from flask import Flask
from flask_hookserver import Hooks

APP = Flask(__name__)
APP.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
APP.config['VALIDATE_IP'] = (os.environ.get('GIT_HOOK_VALIDATE_IP', 'True').lower() not in ['false', '0'])
APP.config['VALIDATE_SIGNATURE'] = (os.environ.get('GIT_HOOK_VALIDATE_SIGNATURE', 'True').lower() not in ['false', '0'])

HOOKS = Hooks(APP, url='/hooks')

# See http://flask.pocoo.org/docs/0.12/patterns/packages/ for information
import app.views  # noqa F401 pylint: disable=wrong-import-position
