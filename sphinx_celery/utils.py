from __future__ import absolute_import, unicode_literals

import sys

__all__ = ['bytes_if_py2']

if sys.version_info[0] >= 3:

    def bytes_if_py2(s):
        return s
else:

    def bytes_if_py2(s):  # noqa
        if isinstance(s, unicode):
            return s.encode()
        return s
