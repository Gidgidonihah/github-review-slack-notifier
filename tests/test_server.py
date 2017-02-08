""" Tests for the main server file. """
from unittest import TestCase
from unittest.mock import patch

import github_hook_server


class ServerTestCase(TestCase):
    """ Our main server testcase. """

    def test_pint(self):
        self.assertEqual(github_hook_server.ping(None, None), 'pong')

    @patch('github_hook_server.notify_reviewer')
    @patch('github_hook_server.validate_review_request')
    def test_valid_pull_request(self, validator, notifier):
        validator.return_value = True
        notifier.return_value = True
        result = github_hook_server.pull_request({}, None)
        self.assertEqual(result, 'Reviewer Notified')

    @patch('github_hook_server.validate_review_request')
    def test_invalid_pull_request(self, validator):
        validator.return_value = False
        result = github_hook_server.pull_request({}, None)
        self.assertRegex(result, 'ignored')
