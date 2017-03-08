#! /usr/bin/env python
""" Our github hook receiving server. """

from app import HOOKS
from app.github import is_valid_pull_request
from app.slack import notify_recipient


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

    if is_valid_pull_request(data):
        notify_recipient(data)
        result = 'Recipient Notified'
    else:
        result = 'Action ({}) ignored'.format(data.get('action'))

    return result
