from __future__ import absolute_import, unicode_literals

import os
import pickle
import re

from sphinx.builders import Builder

ERR_INVALID_REGEX = 'Invalid regex {0!r} in apicheck_ignore_modules: {1!r}'


class BaseBuilder(Builder):

    def get_outdated_docs(self):
        return '{0} overview'.format(self.name)

    def finish(self):
        picklepath = os.path.join(self.outdir, self.pickle_filename)
        with open(picklepath, mode='wb') as fh:
            pickle.dump(self.as_dict(), fh)

    def compile_regex(self, regex):
        if not regex.startswith('^'):
            regex = '^{0}'.format(regex)
        if not regex.endswith('$'):
            regex = '{0}$'.format(regex)
        try:
            return re.compile(regex)
        except Exception as exc:
            self.warn(ERR_INVALID_REGEX.format(regex, exc))

    def compile_regexes(self, regexes):
        return [self.compile_regex(regex) for regex in regexes]
