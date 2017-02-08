""" Code related to slack webhooks and API calls. """

import datetime
import os
import logging
import math

from slackclient import SlackClient

from app.github import lookup_github_full_name
from app.github import GithubWebhookPayloadParser
from app.octocats import get_random_octocat_image


def notify_reviewer(data):
    """ Compile the necessary information and send a slack notification. """
    payload = _create_slack_message_payload(data)
    _send_slack_message(payload)


def _create_slack_message_payload(data):
    payload_parser = GithubWebhookPayloadParser(data)

    channel = _get_notification_channel(data)

    pull_request_url = payload_parser.get_pull_request_url()
    pull_request_title = payload_parser.get_pull_request_title() or 'Unknown Title'
    pull_request_repo = payload_parser.get_pull_request_repo() or 'Unknown'
    pull_request_number = payload_parser.get_pull_request_number() or math.pi
    pull_request_author_image = payload_parser.get_pull_request_author_image()
    pull_request_description = payload_parser.get_pull_request_description()

    pull_request_author = _get_slack_username_by_github_username(payload_parser.get_pull_request_author())
    if pull_request_author:
        pull_request_author = '@{}'.format(pull_request_author)
    else:
        pull_request_author = 'someone'

    msg_text = "You've been asked by {} to review a pull request. Lucky you!".format(pull_request_author)
    if not channel:
        channel = os.environ.get('DEFAULT_NOTIFICATION_CHANNEL')
        github_username = _get_unmatched_username(data)
        msg_text = '{}! {}'.format(github_username, msg_text)

    message = {
        "text": msg_text,
        "as_user": True,
        "link_names": True,
        "attachments": [
            {
                "fallback": "<{}|{}>".format(pull_request_url, pull_request_title),
                "color": "#36a64f",
                "author_name": "{} pull request #{}".format(pull_request_repo, pull_request_number),
                "author_link": pull_request_url,
                "author_icon": "https://github.com/favicon.ico",
                "title": pull_request_title,
                "title_link": pull_request_url,
                "text": pull_request_description,
                "thumb_url": get_random_octocat_image(),
                "footer": "Github PR Notifier",
                "footer_icon": pull_request_author_image,
                "ts": int(datetime.datetime.now().timestamp())
            }
        ]
    }
    if channel:
        message['channel'] = channel

    return message


def _get_notification_channel(data):
    payload_parser = GithubWebhookPayloadParser(data)
    slack_username = _get_slack_username_by_github_username(payload_parser.get_request_reviewer_username())

    if slack_username:
        channel = '@{}'.format(slack_username)
    else:
        channel = None

    return channel


def _get_slack_username_by_github_username(github_username):  # pylint: disable=invalid-name
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    response = slack_client.api_call("users.list")
    users = response.get('members', [])

    if github_username:
        slack_username = _match_slack_github_username(users, github_username)
        if not slack_username:
            full_name = lookup_github_full_name(github_username)
            slack_username = _match_slack_un_by_fullname(users, full_name)
        return slack_username
    else:
        return None


def _match_slack_github_username(users, github_username):
    for user in users:
        if isinstance(user, dict) and user.get('name').lower() == github_username.lower():
            return user.get('name')
    return None


def _match_slack_un_by_fullname(users, full_name):
    if full_name:
        for user in users:
            if isinstance(user, dict) and user.get('real_name', '').lower() == full_name.lower():
                return user.get('name')
    return None


def _get_unmatched_username(data):
    payload_parser = GithubWebhookPayloadParser(data)
    github_username = payload_parser.get_request_reviewer_username()
    if github_username is not None:
        return '@{}'.format(github_username)
    else:
        return 'Hey you, tech guys'


def _send_slack_message(payload):
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    response = slack_client.api_call("chat.postMessage", **payload)

    logger = logging.getLogger(__name__)
    if not response.get('ok'):
        logger.warning('Unable to send message. Response: %s\nPayload:\n%s', response, payload)
    else:
        logger.info('Success!')
