from __future__ import absolute_import, unicode_literals

from .utils import bytes_if_py2


def setup(app):
    app.add_crossref_type(
        directivename=bytes_if_py2('setting'),
        rolename=bytes_if_py2('setting'),
        indextemplate=bytes_if_py2('pair: %s; setting'),
    )

    return {
        'parallel_read_safe': True
    }
