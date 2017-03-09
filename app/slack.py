""" Code related to slack webhooks and API calls. """

import datetime
import logging
import math
import os

from slackclient import SlackClient

from app.github import GithubWebhookPayloadParser
from app.github import get_recipient_github_username_by_action
from app.github import lookup_github_full_name
from app.octocats import get_random_octocat_image


def notify_recipient(data):
    """ Compile the necessary information and send a slack notification. """
    payload = _create_slack_message_payload(data)
    _send_slack_message(payload)


def _create_slack_message_payload(data):
    pr_metadata = _get_pull_request_metadata(data)

    msg_text = _get_message(pr_metadata, data)
    message = _build_payload(msg_text, pr_metadata)

    return message


def _get_message(pr_metadata, data):

    if data.get('action') == 'review_requested':
        action_msg = 'asked by {author} to review a pull request'.format(author=pr_metadata.get('author'))
    elif data.get('action') == 'assigned':
        action_msg = 'assigned a pull request by {author}'.format(author=pr_metadata.get('author'))
    else:
        action_msg = 'pinged'

    msg_text = "You've been {action}. Lucky you!".format(action=action_msg)
    if pr_metadata.get('channel') == os.environ.get('DEFAULT_NOTIFICATION_CHANNEL'):
        github_username = _get_unmatched_username(data)
        msg_text = '{}! {}'.format(github_username, msg_text)

    return msg_text


def _build_payload(msg_text, pr_metadata):
    message = {
        "text": msg_text,
        "as_user": True,
        "link_names": True,
        "channel": pr_metadata.get('channel'),
        "attachments": [
            {
                "fallback": "<{}|{}>".format(pr_metadata.get('url'), pr_metadata.get('title')),
                "color": "#36a64f",
                "author_name": "{} pull request #{}".format(pr_metadata.get('repo'), pr_metadata.get('number')),
                "author_link": pr_metadata.get('url'),
                "author_icon": "https://github.com/favicon.ico",
                "title": pr_metadata.get('title'),
                "title_link": pr_metadata.get('url'),
                "text": pr_metadata.get('description'),
                "thumb_url": get_random_octocat_image(),
                "footer": "Github PR Notifier",
                "footer_icon": pr_metadata.get('author_image'),
                "ts": int(datetime.datetime.now().timestamp())
            }
        ]
    }
    return message


def _get_pull_request_metadata(data):
    pull_request_data = {}
    payload_parser = GithubWebhookPayloadParser(data)

    pull_request_data['url'] = payload_parser.get_pull_request_url()
    pull_request_data['title'] = payload_parser.get_pull_request_title() or 'Unknown Title'
    pull_request_data['repo'] = payload_parser.get_pull_request_repo() or 'Unknown'
    pull_request_data['number'] = payload_parser.get_pull_request_number() or math.pi
    pull_request_data['author_image'] = payload_parser.get_pull_request_author_image()
    pull_request_data['description'] = payload_parser.get_pull_request_description()
    pull_request_data['channel'] = _get_notification_channel(data)

    pull_request_author = _get_slack_username_by_github_username(payload_parser.get_pull_request_author())

    if pull_request_author:
        pull_request_author = '@{}'.format(pull_request_author)
    else:
        pull_request_author = 'someone'

    pull_request_data['author'] = pull_request_author

    return pull_request_data


def _get_notification_channel(data):
    github_username = get_recipient_github_username_by_action(data)
    slack_username = _get_slack_username_by_github_username(github_username)

    if slack_username:
        channel = '@{}'.format(slack_username)
    else:
        channel = os.environ.get('DEFAULT_NOTIFICATION_CHANNEL')

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
