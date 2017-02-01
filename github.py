""" Code related to github webhooks and API calls. """

import os

import requests
from werkzeug.exceptions import BadRequest


def validate_review_request(data):
    """ Verify that the request from github is a valid review request. """

    if 'action' not in data:
        raise BadRequest('no event supplied')

    # Handle only review_requested actions
    if data.get('action') == 'review_requested':
        if 'pull_request' not in data or 'html_url' not in data.get('pull_request'):
            raise BadRequest('payload.pull_request.html_url missing')
        return True
    else:
        return False


def lookup_github_full_name(gh_username):
    """ Retrieve a github user's full name by username. """
    url = 'https://api.github.com/users/{}'.format(gh_username)
    request = requests.get(url, auth=(os.environ.get('GITHUB_API_USER'), os.environ.get('GITHUB_API_TOKEN')))
    user = request.json()
    return user.get('name', '')
