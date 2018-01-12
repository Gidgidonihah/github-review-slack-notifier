# pylint: disable=invalid-name, too-many-arguments, protected-access
""" Test for the slack module. """
import datetime
import os
from unittest import TestCase
from unittest import skipUnless
from unittest.mock import patch

from werkzeug.exceptions import BadRequest

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
    def test_notify_recipient_on_network(self):
        """ Full integration test on the network. """
        with self.assertLogs('app.slack', level='INFO'):
            slack.notify_recipient({})

    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack.lookup_github_full_name')
    @patch('slackclient.SlackClient.api_call')
    def test_notify_recipient(self, slack_client, get_name, get_octocat):
        """ Full integration test. """
        slack_client.return_value = {'ok': False, 'error': 'not_authed'}
        get_name.return_value = FULL_NAME
        get_octocat.return_value = 'octocat'

        with self.assertLogs('app.slack', level='WARNING'):
            slack.notify_recipient(SAMPLE_GITHUB_PAYLOAD)

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    @patch('app.slack._get_notification_channel')
    def test_create_full_review_slack_message_payload(self, get_channel, get_username, get_unbygh,
                                                      get_octocat, get_env):
        """ Should create a fully valid slack message payload. """
        get_channel.return_value = '#leia'
        get_username.return_value = '@luke'
        get_unbygh.return_value = 'obiwan'
        get_octocat.return_value = 'octocat'
        get_env.return_value = '#default-channel'

        payload = slack._create_slack_message_payload(SAMPLE_GITHUB_PAYLOAD)

        self.assertEqual(payload.get('text'), "You've been asked by @obiwan to review a pull request. Lucky you!")
        self.assertTrue(payload.get('as_user'))
        self.assertTrue(payload.get('link_names'))
        self.assertEqual(payload.get('channel'), '#leia')

        attachment = payload.get('attachments')[0]
        self.assertEqual(attachment.get('fallback'), "<http://www.example.com|PR Title>")
        self.assertEqual(attachment.get('color'), '#36a64f')
        self.assertEqual(attachment.get('author_name'), 'Example Repository pull request #1')
        self.assertEqual(attachment.get('author_link'), 'http://www.example.com')
        self.assertEqual(attachment.get('author_icon'), 'https://github.com/favicon.ico')
        self.assertEqual(attachment.get('title'), 'PR Title')
        self.assertEqual(attachment.get('title_link'), 'http://www.example.com')
        self.assertEqual(attachment.get('text'), 'An example pull request.')
        self.assertEqual(attachment.get('thumb_url'), 'octocat')
        self.assertEqual(attachment.get('footer'), 'Github PR Notifier')
        self.assertEqual(attachment.get('footer_icon'), 'https://github.com/apple-touch-icon-180x180.png')
        self.assertEqual(attachment.get('ts'), int(datetime.datetime.now().timestamp()))

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    @patch('app.slack._get_notification_channel')
    def test_create_assignment_slack_message_payload(self, get_channel, get_username, get_unbygh, get_octocat, get_env):
        """ Should create a fully valid slack message payload. """
        get_channel.return_value = '#leia'
        get_username.return_value = '@luke'
        get_unbygh.return_value = 'obiwan'
        get_octocat.return_value = 'octocat'
        get_env.return_value = '#default-channel'

        request_payload = SAMPLE_GITHUB_PAYLOAD.copy()
        request_payload['action'] = 'assigned'

        payload = slack._create_slack_message_payload(request_payload)
        self.assertEqual(payload.get('text'), "You've been assigned a pull request by @obiwan. Lucky you!")

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    def test_create_slack_review_message_payload_with_default_channel(self, get_username, get_unbygh,
                                                                      get_octocat, get_env):
        """ Should create a slack payload with a default (env var) channel. """
        get_username.return_value = '@luke'
        get_unbygh.return_value = None
        get_octocat.return_value = 'octocat'
        get_env.return_value = '#default-channel'

        payload = slack._create_slack_message_payload(SAMPLE_GITHUB_PAYLOAD)
        self.assertEqual(payload.get('channel'), get_env.return_value)

    @patch('os.environ.get')
    @patch('app.slack.get_random_octocat_image')
    @patch('app.slack._get_slack_username_by_github_username')
    @patch('app.slack._get_unmatched_username')
    def test_create_review_slack_message_payload_with_no_data(self, get_username, get_unbygh, get_octocat, get_env):
        """ Should raise a BadRequest Exception. """
        get_octocat.return_value = 'octocat'
        get_env.return_value = None
        get_username.return_value = None
        get_unbygh.return_value = None

        with self.assertRaises(BadRequest):
            slack._create_slack_message_payload({})

    @patch('os.environ.get')
    def test_get_message(self, get_env):
        """ Should test all permutations of messages. """

        pinged_message = slack._get_message({}, {})
        self.assertEqual("You've been pinged. Lucky you!", pinged_message)

        review_message = slack._get_message({'author': GENERIC_USERNAME}, {'action': 'review_requested'})
        expected_message = "You've been asked by big_daddy_bob to review a pull request. Lucky you!"
        self.assertEqual(expected_message, review_message)

        assigned_message = slack._get_message({'author': GENERIC_USERNAME}, {'action': 'assigned'})
        expected_message = "You've been assigned a pull request by big_daddy_bob. Lucky you!"
        self.assertEqual(expected_message, assigned_message)

        get_env.return_value = '#hello'
        pr_metadata = {'author': GENERIC_USERNAME, 'channel': get_env.return_value}
        default_channel_message = slack._get_message(pr_metadata, {'action': 'review_requested'})
        expected_message = "Hey you, tech guys! You've been asked by big_daddy_bob to review a pull request. Lucky you!"
        self.assertEqual(expected_message, default_channel_message)

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
