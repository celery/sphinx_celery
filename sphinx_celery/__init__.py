"""Sphinx Celery Theme."""
from __future__ import absolute_import, unicode_literals

import os

from collections import namedtuple

version_info_t = namedtuple(
    'version_info_t', ('major', 'minor', 'micro', 'releaselevel', 'serial'),
)

VERSION = version_info = version_info_t(1, 0, 0, '', '')

__version__ = '{0.major}.{0.minor}.{0.micro}{0.releaselevel}'.format(VERSION)
__author__ = 'Ask Solem'
__contact__ = 'ask@celeryproject.org'
__homepage__ = 'http://github.com/celery/sphinx_celery'
__docformat__ = 'restructuredtext'

# -eof meta-

__all__ = ['get_html_templates_path', 'get_html_theme_path']


def get_html_theme_path():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_html_templates_path():
    return os.path.join(
        os.path.abspath(os.path.dirname((__file__))),
        'templates',
    )
