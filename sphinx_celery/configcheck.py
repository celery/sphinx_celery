"""

Sphinx Configuration Reference Checker
======================================

This builder extension makes sure all settings in the documented
package are represented in the configuration reference (
meaning they all have ``.. setting::`` directives).

Usage
-----

.. code-block:: console

    $ sphinx-build -b configcheck -d _build/doctrees . _build/configcheck

Configuration
-------------

configcheck_ignore_settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

List of settings to ignore, either as setting names or regexes.

Example:

.. code-block:: python

    configcheck_ignore_settings = [
        'USE_TZ',
        r'.*SECRET.*',
    ]

configcheck_project_settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A function returning a set of all setting names.

Example:

.. code-block:: python

    def configcheck_project_settings():
        from django import conf

        return set(conf._all_settings)


configcheck_should_ignore
~~~~~~~~~~~~~~~~~~~~~~~~~

Optional function that can be used in addition to
``configcheck_ignore_settings`` to ignore setting names programmatically.


Example:

.. code-block:: python

    def configcheck_should_ignore(setting):
        from django import conf
        return conf.is_deprecated(setting)


"""
from __future__ import absolute_import, unicode_literals

from six import iterkeys as keys

from sphinx.util.console import bold, green, red

from .builders import BaseBuilder
from .utils import bytes_if_py2

ERR = 'ERROR'
ERR_MISSING_DOC = '{error}: Setting not documented: {name}'
OK_STATUS = 'OK: All settings documented :o)'


class ConfigCheckBuilder(BaseBuilder):
    name = 'configcheck'
    pickle_filename = 'configcheck.pickle'

    def init(self):
        self.ignore_patterns = self.compile_regexes(
            self.config.configcheck_ignore_settings,
        )
        self.should_ignore = (
            self.config.configcheck_should_ignore or (lambda s: False))
        self.project_settings = self.config.configcheck_project_settings
        self.undocumented = set()

    def is_ignored_setting(self, setting):
        return self.should_ignore(setting) or any(
            regex.match(setting) for regex in self.ignore_patterns)

    def write(self, *ignored):
        self.check_missing()

    def documented_settings(self):
        return {
            name for reftype, name in keys(
                self.app.env.domaindata['std']['objects'])
            if reftype == 'setting'
        }

    def check_missing(self):
        all_settings = self.project_settings()
        documented_settings = self.documented_settings()
        self.undocumented.update(
            setting for setting in all_settings ^ documented_settings
            if not self.is_ignored_setting(setting)
        )

        for setting in self.undocumented:
            self.app.statuscode = 2
            print(ERR_MISSING_DOC.format(
                error=red(ERR),
                name=bold(setting),
            ))
        if not self.app.statuscode:
            print(green(OK_STATUS))

    def as_dict(self):
        return {
            'undocumented': self.undocumented,
        }


def setup(app):
    app.add_builder(ConfigCheckBuilder)
    app.add_config_value(
        bytes_if_py2('configcheck_ignore_settings'), [], False)
    app.add_config_value(
        bytes_if_py2('configcheck_project_settings'), None, False)
    app.add_config_value(
        bytes_if_py2('configcheck_should_ignore'), None, False)

    return {
        'parallel_read_safe': True
    }
