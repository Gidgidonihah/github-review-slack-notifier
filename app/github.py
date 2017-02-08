""" Code related to github webhooks and API calls. """

import copy
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
    request = requests.get(url, auth=(os.environ.get('GITHUB_API_USER', ''), os.environ.get('GITHUB_API_TOKEN', '')))
    user = request.json()
    return user.get('name', '')


class GithubWebhookPayloadParser(object):
    """ A class to parse a github payload and return specific elements. """

    def __init__(self, data=None):
        if data is None:
            data = {}
        self._data = copy.deepcopy(data)

    def get_request_reviewer_username(self):
        """ Parse and retrieve the requested reviewer username. """
        return self._data.get('requested_reviewer', {}).get('login')

    def get_pull_request_title(self):
        """ Parse and retrieve the pull request title. """
        return self._data.get('pull_request', {}).get('title')

    def get_pull_request_url(self):
        """ Parse and retrieve the pull request html url. """
        return self._data.get('pull_request', {}).get('html_url')

    def get_pull_request_repo(self):
        """ Parse and retrieve the pull request repository name. """
        return self._data.get('repository', {}).get('full_name')

    def get_pull_request_number(self):
        """ Parse and retrieve the pull request number. """
        return self._data.get('number')

    def get_pull_request_author(self):
        """ Parse and retrieve the pull request author. """
        return self._data.get('pull_request', {}).get('user', {}).get('login')

    def get_pull_request_author_image(self):
        """ Parse and retrieve the pull request author image. """
        return self._data.get('pull_request', {}).get('user', {}).get('avatar_url')

    def get_pull_request_description(self):
        """ Parse and retrieve the pull request repository description. """
        return self._data.get('pull_request', {}).get('body')
