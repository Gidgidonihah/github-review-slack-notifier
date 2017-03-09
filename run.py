#! /usr/bin/env python
""" Our github hook receiving server. """

from app import APP

APP.run(host='0.0.0.0')
