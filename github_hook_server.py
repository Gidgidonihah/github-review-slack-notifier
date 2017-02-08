#! /usr/bin/env python
""" Our github hook receiving server. """

import os

from flask import Flask
from flask_hookserver import Hooks

from app.github import validate_review_request
from app.slack import notify_reviewer

APP = Flask(__name__)
APP.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
if os.environ.get('GIT_HOOK_VALIDATE_IP', 'True').lower() in ['false', '0']:
    APP.config['VALIDATE_IP'] = False
if os.environ.get('GIT_HOOK_VALIDATE_SIGNATURE', 'True').lower() in ['false', '0']:
    APP.config['VALIDATE_SIGNATURE'] = False

HOOKS = Hooks(APP, url='/hooks')


@HOOKS.hook('ping')
def ping(_data, _guid):
    return 'pong'


@HOOKS.hook('pull_request')
def pull_request(data, _guid):
    """
    Handle a pull request webhook and notify the reviewer on slack.

    This will validate the request making sure it is an action that is written to be handled,
    then will kick off apropriate actions for the hook such as sending slack notifications
    to the requested reviewer.
    """

    if validate_review_request(data):
        notify_reviewer(data)
        result = 'Reviewer Notified'
    else:
        result = 'Action ({}) ignored'.format(data.get('action'))

    return result


if __name__ == "__main__":
    APP.run(host='0.0.0.0')
