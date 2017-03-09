""" Tests for the main server file. """
from unittest import TestCase
from unittest.mock import patch

from app import views


class ViewsTestCase(TestCase):
    """ Our main server testcase. """

    def test_ping(self):
        self.assertEqual(views.ping(None, None), 'pong')

    @patch('app.views.notify_recipient')
    @patch('app.views.is_valid_pull_request')
    def test_valid_pull_request(self, validator, notifier):
        validator.return_value = True
        notifier.return_value = True
        result = views.pull_request({}, None)
        self.assertEqual(result, 'Recipient Notified')

    @patch('app.views.is_valid_pull_request')
    def test_invalid_pull_request(self, validator):
        validator.return_value = False
        result = views.pull_request({}, None)
        self.assertRegex(result, 'ignored')
