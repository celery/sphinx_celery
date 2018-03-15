"""Sphinx Celery Theme."""
from __future__ import absolute_import, unicode_literals

import os
import re

from collections import namedtuple

__version__ = '1.4.0'
__author__ = 'Ask Solem'
__contact__ = 'ask@celeryproject.org'
__homepage__ = 'http://github.com/celery/sphinx_celery'
__docformat__ = 'restructuredtext'

# -eof meta-

__all__ = ['get_html_templates_path', 'get_html_theme_path']

version_info_t = namedtuple('version_info_t', (
    'major', 'minor', 'micro', 'releaselevel', 'serial',
))

# bumpversion can only search for {current_version}
# so we have to parse the version here.
_temp = re.match(
    r'(\d+)\.(\d+).(\d+)(.+)?', __version__).groups()
VERSION = version_info = version_info_t(
    int(_temp[0]), int(_temp[1]), int(_temp[2]), _temp[3] or '', '')
del(_temp)
del(re)


def get_html_theme_path():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_html_templates_path():
    return os.path.join(
        os.path.abspath(os.path.dirname((__file__))),
        'templates',
    )
