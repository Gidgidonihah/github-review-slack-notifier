#! /usr/bin/env python
""" Our github hook receiving server. """

import os

from flask import Flask
from flask_hookserver import Hooks

from github import validate_review_request
from slack import notify_reviewer

app = Flask(__name__)
app.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
if os.environ.get('GIT_HOOK_VALIDATE_IP', 'True').lower() in ['false', '0']:
    app.config['VALIDATE_IP'] = False
if os.environ.get('GIT_HOOK_VALIDATE_SIGNATURE', 'True').lower() in ['false', '0']:
    app.config['VALIDATE_SIGNATURE'] = False

hooks = Hooks(app, url='/hooks')


@hooks.hook('ping')
def ping(data, guid):
    return 'pong'


@hooks.hook('pull_request')
def pull_request(data, guid):

    if validate_review_request(data):
        notify_reviewer(data)
        result = 'Reviewer Notified'
    else:
        result = 'Action ({}) ignored'.format(data.get('action'))

    return result


app.run(host='0.0.0.0')
