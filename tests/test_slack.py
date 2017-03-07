# pylint: disable=invalid-name, too-many-arguments, protected-access
""" Test for the slack module. """
import datetime
import os
from unittest import TestCase
from unittest import skipUnless
from unittest.mock import patch

from app import slack
from tests.test_github import FULL_NAME
from tests.test_github import GENERIC_USERNAME
from tests.test_github import SAMPLE_GITHUB_PAYLOAD


class SlackTest(TestCase):
    """
    Main slack module testcase.

    Any tests that require network access should be patched or wrapped with a skipunless.
    You may run these test by adding the appropriate tokens and environment variables.
    """

    USERS = [{
        'real_name': FULL_NAME.upper(),
        'name': GENERIC_USERNAME,
    }]

    @skipUnless(os.environ.get('GITHUB_API_USER')
                and os.environ.get('GITHUB_API_TOKEN')
                and os.environ.get('SLACK_BOT_TOKEN'),
                "valid slack and github tokens needed")
    @skipUnless(os.environ.get('TEST_ON_NETWORK'), "Network tests ignored")
    def test_notify_reviewer_on_network(self):
        """ Full integration test on the network. """
        with self.assertLogs('app.slack', level='INFO'):
            slack.notify_reviewer({})

    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack.lookup_github_full_name')
    @patch('slackclient.SlackClient.api_call')
    def test_notify_reviewer(self, slack_client, get_name, get_octocat):
        """ Full integration test. """
        slack_client.return_value = {'ok': False, 'error': 'not_authed'}
        get_name.return_value = FULL_NAME
        get_octocat.return_value = 'octocat'

        with self.assertLogs('app.slack', level='WARNING'):
            slack.notify_reviewer(SAMPLE_GITHUB_PAYLOAD)

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    @patch('app.slack._get_notification_channel')
    def test_create_slack_message_payload(self, get_channel, get_username, get_unbygh, get_octocat, get_env):
        """ Should create a fully valid slack message payload. """
        get_channel.return_value = '#leia'
        get_username.return_value = '@luke'
        get_unbygh.return_value = 'obiwan'
        get_octocat.return_value = 'octocat'
        get_env.return_value = '#default-channel'

        payload = slack._create_slack_message_payload(SAMPLE_GITHUB_PAYLOAD)
        generated_payload = {'text': "You've been asked by @obiwan to review a pull request. Lucky you!", 'as_user': True, 'link_names': True, 'attachments': [{'fallback': '<http://www.example.com|PR Title>', 'color': '#36a64f', 'author_name': 'Example Repository pull request #1', 'author_link': 'http://www.example.com', 'author_icon': 'https://github.com/favicon.ico', 'title': 'PR Title', 'title_link': 'http://www.example.com', 'text': 'An example pull request.', 'thumb_url': 'octocat', 'footer': 'Github PR Notifier', 'footer_icon': 'https://github.com/apple-touch-icon-180x180.png', 'ts': int(datetime.datetime.now().timestamp())}], 'channel': '#leia'}  # noqa: E501, pylint: disable=line-too-long
        self.assertDictEqual(payload, generated_payload)

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    def test_create_slack_message_payload_with_default_channel(self, get_username, get_unbygh, get_octocat, get_env):
        """ Should create a slack payload with a default (env var) channel. """
        get_username.return_value = '@luke'
        get_unbygh.return_value = None
        get_octocat.return_value = 'octocat'
        get_env.return_value = '#default-channel'

        payload = slack._create_slack_message_payload(SAMPLE_GITHUB_PAYLOAD)
        generated_payload = {'text': "@luke! You've been asked by someone to review a pull request. Lucky you!", 'as_user': True, 'link_names': True, 'attachments': [{'fallback': '<http://www.example.com|PR Title>', 'color': '#36a64f', 'author_name': 'Example Repository pull request #1', 'author_link': 'http://www.example.com', 'author_icon': 'https://github.com/favicon.ico', 'title': 'PR Title', 'title_link': 'http://www.example.com', 'text': 'An example pull request.', 'thumb_url': 'octocat', 'footer': 'Github PR Notifier', 'footer_icon': 'https://github.com/apple-touch-icon-180x180.png', 'ts': int(datetime.datetime.now().timestamp())}], 'channel': '#default-channel'}  # noqa: E501, pylint: disable=line-too-long
        self.assertDictEqual(payload, generated_payload)

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    def test_create_slack_message_payload_with_no_data(self, get_username,
                                                       get_unbygh, get_octocat, get_env):
        """ Should create a slack message without any data. """
        get_octocat.return_value = 'octocat'
        get_env.return_value = None
        get_username.return_value = None
        get_unbygh.return_value = None

        payload = slack._create_slack_message_payload({})
        generated_payload = {'text': "None! You've been asked by someone to review a pull request. Lucky you!", 'as_user': True, 'link_names': True, 'attachments': [{'fallback': '<None|Unknown Title>', 'color': '#36a64f', 'author_name': 'Unknown pull request #3.141592653589793', 'author_link': None, 'author_icon': 'https://github.com/favicon.ico', 'title': 'Unknown Title', 'title_link': None, 'text': None, 'thumb_url': 'octocat', 'footer': 'Github PR Notifier', 'footer_icon': None, 'ts': int(datetime.datetime.now().timestamp())}], 'channel': None}  # noqa: E501, pylint: disable=line-too-long
        self.assertDictEqual(payload, generated_payload)

    @patch('app.slack._get_slack_username_by_github_username')
    def test_get_notification_channel(self, username_getter):
        """ Test getting the notification channel. """
        username_getter.return_value = GENERIC_USERNAME
        channel = slack._get_notification_channel(SAMPLE_GITHUB_PAYLOAD)
        self.assertEqual(channel, '@{}'.format(GENERIC_USERNAME))

        username_getter.return_value = None
        channel = slack._get_notification_channel(SAMPLE_GITHUB_PAYLOAD)
        self.assertIsNone(channel)

    @patch('app.slack.lookup_github_full_name')
    @patch('slackclient.SlackClient.api_call')
    def test_get_slack_username_by_github_username_with_match(self, slack_client, name_lookup):
        """ Test getting a matching slack and github username. """
        slack_client.return_value = {'members': self.USERS}
        name_lookup.return_value = FULL_NAME
        username = slack._get_slack_username_by_github_username(GENERIC_USERNAME)
        self.assertEqual(username, GENERIC_USERNAME)

    @patch('app.slack.lookup_github_full_name')
    @patch('slackclient.SlackClient.api_call')
    def test_get_slack_username_by_github_username_without_match(self, slack_client, name_lookup):
        """ Test getting a slack username without a match from github. """
        different_username = 'gibberish'
        modified_user = self.USERS[0].copy()
        modified_user.update({'name': different_username})
        slack_client.return_value = {'members': [modified_user]}
        name_lookup.return_value = FULL_NAME

        username = slack._get_slack_username_by_github_username(GENERIC_USERNAME)
        self.assertEqual(username, different_username)

    @patch('app.slack.lookup_github_full_name')
    @patch('slackclient.SlackClient.api_call')
    def test_get_slack_username_by_github_username_without_username(self, slack_client, name_lookup):
        """ Test getting a slack username without a name passed in. """
        slack_client.return_value = {'members': self.USERS}
        name_lookup.return_value = FULL_NAME

        username = slack._get_slack_username_by_github_username(None)
        self.assertIsNone(username)

    def test_match_slack_github_username(self):
        """ Test matching a slack and github username. """
        name = slack._match_slack_github_username(self.USERS, GENERIC_USERNAME)
        self.assertEqual(name, GENERIC_USERNAME)

        users = []
        name = slack._match_slack_github_username(users, GENERIC_USERNAME)
        self.assertIsNone(name)

    def test_match_slack_un_by_fullname(self):
        """ Test matching a slack and github user by full name. """
        name = slack._match_slack_un_by_fullname(self.USERS, FULL_NAME)
        self.assertEqual(name, GENERIC_USERNAME)

        users = []
        name = slack._match_slack_un_by_fullname(users, FULL_NAME)
        self.assertIsNone(name)

    def test_get_unmatched_username(self):
        """ Test getting an unmatched username. """
        name = slack._get_unmatched_username(SAMPLE_GITHUB_PAYLOAD)
        self.assertEqual(name, '@{}'.format(GENERIC_USERNAME))

        name = slack._get_unmatched_username({})
        self.assertEqual(name, 'Hey you, tech guys')

    @patch('slackclient.SlackClient.api_call')
    def test_send_slack_message(self, slack_client):
        slack_client.return_value = {'ok': False, 'error': 'not_authed'}
        with self.assertLogs('app.slack', level='WARNING'):
            slack._send_slack_message({})

    @patch('slackclient.SlackClient.api_call')
    def test_send_slack_message_success(self, slack_client):
        slack_client.return_value = {'ok': True}
        with self.assertLogs('app.slack', level='INFO'):
            slack._send_slack_message({})
