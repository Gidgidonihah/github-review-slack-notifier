# pylint: disable=protected-access
""" Tests for the github module. """
import datetime
import io
import os
from unittest import TestCase
from unittest import skipUnless
from unittest.mock import patch

import app.octocats
from app.octocats import RSS_FILE


class OctocatTest(TestCase):
    """ Test the octocat module. """

    OCTOCAT = 'http://octodex.github.com/images/catstello.png'

    def setUp(self):
        if os.path.exists(RSS_FILE):
            os.remove(RSS_FILE)

    @patch('feedparser.parse')
    @patch('urllib.request.urlopen')
    def test_get_random_octocat_image_offline(self, request, parser):
        """ Full integration test of getting an octocat image. """
        request.return_value = io.BytesIO(b"Octocats")
        parser.return_value = {'entries': [{'summary': self.OCTOCAT}]}
        cat = app.octocats.get_random_octocat_image()
        self.assertRegex(cat, r"https?://octodex.github.com/images/[^\/]*\.[png|jpg|gif]")

    @skipUnless(os.environ.get('TEST_ON_NETWORK'), "Network tests ignored")
    def test_get_random_octocat_image(self):
        """ Full integration test of getting an octocat image. """
        cat = app.octocats.get_random_octocat_image()
        self.assertRegex(cat, r"https?://octodex.github.com/images/[^\/]*\.[png|jpg|gif]")

    @patch('urllib.request.urlopen')
    def test_retrieve_rss_file(self, request):
        """ Test downloading the rss file. """
        request.return_value = io.BytesIO(b"Octocats")
        app.octocats._retrieve_rss_file()
        self.assertTrue(os.path.exists(RSS_FILE))
        with open(RSS_FILE) as file:
            self.assertEqual(file.read(), 'Octocats')

    @patch('os.path.getmtime')
    @patch('os.path.exists')
    def test_should_retrieve_rss_file(self, path_exists, mtimecheck):
        """ Test the logic asking should the rss file be retrieved. """
        path_exists.return_value = False
        self.assertTrue(app.octocats._should_retrieve_rss_file())

        path_exists.return_value = True
        mtimecheck.return_value = datetime.datetime.now().timestamp()
        self.assertFalse(app.octocats._should_retrieve_rss_file())

        mtimecheck.return_value = datetime.datetime.now().timestamp() - 60*60*24*7
        self.assertTrue(app.octocats._should_retrieve_rss_file())

    @patch('os.path.getmtime')
    def test_is_file_not_older_than_7_days(self, mtimecheck):
        """ Test the file age test logic. """
        mtimecheck.return_value = datetime.datetime.now().timestamp()
        self.assertFalse(app.octocats._is_file_older_than_7_days('omgwtfbbq'))

        mtimecheck.return_value = datetime.datetime.now().timestamp() - 60*60*24*7
        self.assertTrue(app.octocats._is_file_older_than_7_days('omgwtfbbq'))

    @patch('feedparser.parse')
    def test_get_octocats_from_rss(self, parser):
        """ Test parsing the rss file for octocat images. """
        parser.return_value = {'entries': [{'summary': self.OCTOCAT}]}
        cats = app.octocats._get_octocats_from_rss()
        self.assertEqual(cats.pop(), self.OCTOCAT)
