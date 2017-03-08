# pylint: disable=invalid-name,protected-access
""" Tests for the github module. """
import os
from unittest import TestCase
from unittest import skipUnless

import responses
from werkzeug.exceptions import BadRequest

from app.github import lookup_github_full_name
from app.github import is_valid_pull_request
# from app.github import validate_assignment_request
from app.github import GithubWebhookPayloadParser


FULL_NAME = 'Bob Barker'
GENERIC_USERNAME = 'big_daddy_bob'
SAMPLE_GITHUB_PAYLOAD = {
    'action': 'review_requested',
    'number': 1,
    'requested_reviewer': {
        'login': GENERIC_USERNAME,
    },
    'pull_request': {
        'body': 'An example pull request.',
        'html_url': 'http://www.example.com',
        'title': 'PR Title',
        'user': {
            'login': GENERIC_USERNAME,
            'avatar_url': 'https://github.com/apple-touch-icon-180x180.png',
        },
    },
    'repository': {
        'full_name': 'Example Repository',
    }
}


class GithubReviewRequestTest(TestCase):
    """ Test the github review request functions. """

    def setUp(self):
        self.valid_request = {
            'action': 'review_requested',
            'pull_request': {
                'html_url': 'https://www.example.com',
            },
        }

    def test_is_valid_pull_request_good(self):
        """ Test a good is_valid_pull_request. """
        is_valid_request = is_valid_pull_request(self.valid_request)
        self.assertTrue(is_valid_request)

    def test_is_valid_pull_request_missing_action(self):
        """ Test with missing action """
        with self.assertRaises(BadRequest):
            data = self.valid_request.copy()
            del data['action']
            is_valid_pull_request(data)

    def test_is_valid_pull_request_missing_pulL_request(self):
        """ Test with missing pull_request dict """
        with self.assertRaises(BadRequest):
            data = self.valid_request.copy()
            del data['pull_request']
            is_valid_pull_request(data)

    def test_is_valid_pull_request_missing_html_url(self):
        """ Test with missing html_url on pull_request dict """
        with self.assertRaises(BadRequest):
            data = self.valid_request.copy()
            data['pull_request'] = {}
            is_valid_pull_request(data)

    def test_is_valid_pull_request_different_action(self):
        """ Test with non matched action """
        data = self.valid_request.copy()
        data['action'] = 'generic_action'
        is_valid_request = is_valid_pull_request(data)
        self.assertFalse(is_valid_request)


class GeneralGithubTest(TestCase):
    """ Test the general github functions. """

    def setUp(self):
        self.gh_username = 'gidgidonihah'
        self.gh_full_name = 'Jason Weir'

    def test_lookup_github_fullname(self):
        """ Test lookup_github_full_name. """
        with responses.RequestsMock() as rsps:
            rsps.add('GET', 'https://api.github.com/users/{}'.format(self.gh_username),
                     json={"name": self.gh_full_name}, status=200)
            name = lookup_github_full_name(self.gh_username)
            self.assertEqual(name, self.gh_full_name)

    @skipUnless(os.environ.get('GITHUB_API_USER') and os.environ.get('GITHUB_API_TOKEN'), "valid github tokens needed")
    @skipUnless(os.environ.get('TEST_ON_NETWORK'), "Network tests ignored")
    def test_network_lookup_github_fullname(self):
        """ Test lookup_github_full_name with a network request to github. """
        name = lookup_github_full_name(self.gh_username)
        self.assertEqual(name, self.gh_full_name)


class GithubWebhookPayloadParserTest(TestCase):
    """ Testcase for the Github webhook parser. """

    def setUp(self):
        self.parser = GithubWebhookPayloadParser(SAMPLE_GITHUB_PAYLOAD)

    def test_init(self):
        self.parser = GithubWebhookPayloadParser()
        self.assertEqual(self.parser._data, {})

    def test_get_request_reviewer_username(self):
        self.assertEqual(self.parser.get_request_reviewer_username(), 'big_daddy_bob')
        del self.parser._data['requested_reviewer']['login']
        self.assertIsNone(self.parser.get_request_reviewer_username())

    def test_get_pull_request_title(self):
        self.assertEqual(self.parser.get_pull_request_title(), 'PR Title')
        del self.parser._data['pull_request']['title']
        self.assertIsNone(self.parser.get_pull_request_title())

    def test_get_pull_request_url(self):
        self.assertEqual(self.parser.get_pull_request_url(), 'http://www.example.com')
        del self.parser._data['pull_request']['html_url']
        self.assertIsNone(self.parser.get_pull_request_url())

    def test_get_pull_request_repo(self):
        self.assertEqual(self.parser.get_pull_request_repo(), 'Example Repository')
        del self.parser._data['repository']['full_name']
        self.assertIsNone(self.parser.get_pull_request_repo())

    def test_get_pull_request_number(self):
        self.assertEqual(self.parser.get_pull_request_number(), 1)
        del self.parser._data['number']
        self.assertIsNone(self.parser.get_pull_request_number())

    def test_get_pull_request_author(self):
        self.assertEqual(self.parser.get_pull_request_author(), 'big_daddy_bob')
        del self.parser._data['pull_request']['user']['login']
        self.assertIsNone(self.parser.get_pull_request_author())

    def test_get_pull_request_author_image(self):
        self.assertEqual(self.parser.get_pull_request_author_image(), 'https://github.com/apple-touch-icon-180x180.png')
        del self.parser._data['pull_request']['user']['avatar_url']
        self.assertIsNone(self.parser.get_pull_request_author_image())

    def test_get_pull_request_description(self):
        self.assertEqual(self.parser.get_pull_request_description(), 'An example pull request.')
        del self.parser._data['pull_request']['body']
        self.assertIsNone(self.parser.get_pull_request_description())
