from __future__ import absolute_import, unicode_literals

from .utils import bytes_if_py2


def setup(app):
    app.add_crossref_type(
        directivename=bytes_if_py2('signal'),
        rolename=bytes_if_py2('signal'),
        indextemplate=bytes_if_py2('pair: %s; signal'),
    )

    return {
        'parallel_read_safe': True
    }
