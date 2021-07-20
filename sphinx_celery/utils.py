from __future__ import absolute_import, unicode_literals

import six

__all__ = ['bytes_if_py2']

if six.PY3:

    def bytes_if_py2(s):
        return s
else:

    def bytes_if_py2(s):
        if isinstance(s, six.text_type):
            return s.encode()
        return s
