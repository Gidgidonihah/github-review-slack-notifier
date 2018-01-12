""" Get an octocat image. """

from datetime import datetime
import os
import random
import re
import shutil
import urllib.request

import feedparser

RSS_FILE = '/tmp/octocats.rss'


def get_random_octocat_image():
    """
    Retrieve the URL for a random octocat image.

    This will retrieve this list of octocats from http://feeds.feedburner.com/Octocats
    It will download that file locally and store it for a week.
    It will parse that file, and get a list of octocat images.
    It will then return 1 of those images.
    """

    _retrieve_rss_file()
    octocats = _get_octocats_from_rss()
    return random.choice(octocats)


def _retrieve_rss_file():
    """ Download the RSS file locally. """
    if _should_retrieve_rss_file():
        with urllib.request.urlopen('http://feeds.feedburner.com/Octocats') as response, open(RSS_FILE, 'wb') as feed:
            shutil.copyfileobj(response, feed)


def _should_retrieve_rss_file():
    """ Check if the file doesn't exist or is older than 7 days. """

    if not os.path.exists(RSS_FILE):
        return True
    elif _is_file_older_than_7_days(RSS_FILE):
        return True

    return False


def _is_file_older_than_7_days(path):
    modified_time = os.path.getmtime(path)
    file_modified_time = datetime.fromtimestamp(modified_time)
    age_delta = datetime.now() - file_modified_time
    return age_delta.days >= 7


def _get_octocats_from_rss():
    """ Parse the RSS looking for the octocat images. """
    octocats = []
    feed = feedparser.parse(RSS_FILE)
    entries = feed.get('entries', [])
    for entry in entries:
        octocats.extend(re.findall('http.?://octodex[^\'"]*', entry.get('summary')))
    return octocats
