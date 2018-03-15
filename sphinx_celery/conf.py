# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import sys

from . import get_html_templates_path

PY3 = sys.version_info[0] >= 3

LINKCODE_URL = 'https://github.com/{proj}/tree/{branch}/{filename}.py'
GITHUB_BRANCH = 'master'

EXTENSIONS = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.extlinks',

    'sphinx_celery.autodocargspec',
    'sphinx_celery.github_issues',
    'sphinx_celery.signal_crossref',
    'sphinx_celery.setting_crossref',
    'sphinx_celery.apicheck',
    'sphinx_celery.configcheck',
]

INTERSPHINX_MAPPING = {
    'python': ('http://docs.python.org/dev/', None),
    'sphinx': ('http://www.sphinx-doc.org/en/stable/', None),
    'kombu': ('http://kombu.readthedocs.io/en/master/', None),
    'celery': ('http://docs.celeryproject.org/en/master', None),
    'djcelery': ('http://django-celery.readthedocs.io/en/latest/', None),
    'cyme': ('http://cyme.readthedocs.io/en/latest/', None),
    'amqp': ('http://amqp.readthedocs.io/en/latest/', None),
    'vine': ('http://vine.readthedocs.io/en/latest/', None),
    'flower': ('http://flower.readthedocs.io/en/latest/', None),
    'redis': ('http://redis-py.readthedocs.io/en/latest/', None),
    'django': ('http://django.readthedocs.io/en/latest/', None),
    'boto': ('http://boto.readthedocs.io/en/latest/', None),
    'sqlalchemy': ('http://sqlalchemy.readthedocs.io/en/latest', None),
    'kazoo': ('http://kazoo.readthedocs.io/en/latest/', None),
    'msgpack': ('http://msgpack-python.readthedocs.io/en/latest/', None),
    'riak': ('http://basho.github.io/riak-python-client/', None),
    'pylibmc': ('http://sendapatch.se/projects/pylibmc/', None),
    'eventlet': ('http://eventlet.net/doc/', None),
    'gevent': ('http://gevent.org/', None),
    'pyOpenSSL': ('http://pyopenssl.readthedocs.io/en/stable/', None),
    'pytest': ('http://doc.pytest.org/en/latest/', None),
    'tox': ('http://tox.readthedocs.io/en/latest', None),
}

string_types = (str,) if PY3 else (basestring,)


def add_paths(config_file, path_additions):
    this = os.path.dirname(os.path.abspath(config_file))

    sys.path.insert(0, os.path.join(this, os.pardir))
    for path in path_additions:
        sys.path.append(os.path.join(this, path))


def configure_django(django_settings, **config):
    if django_settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings
    else:
        from django.conf import settings  # noqa
        if not settings.configured:
            settings.configure(**config)
    try:
        from django import setup as django_setup
    except ImportError:
        pass
    else:
        django_setup()


def import_package(package):
    if isinstance(package, string_types):
        return __import__(package)
    return package


def prepare_intersphinx_mapping(project, mapping,
                                include, exclude, **extra):
    if include:
        mapping = dict((k, v) for k, v in mapping.items() if k in include)
    if exclude:
        mapping = dict((k, v) for k, v in mapping.items() if k not in exclude)
    mapping = dict(mapping, **extra)

    # Remove project itself from intersphinx
    mapping.pop(project.lower(), None)

    return mapping


def create_linkcode_resolver(linkcode_url, github_project, github_branch):
    def linkcode_resolve(domain, info):
        if domain != 'py' or not info['module']:
            return
        filename = info['module'].replace('.', '/')
        return linkcode_url.format(
            proj=github_project,
            branch=github_branch,
            filename=filename,
        )
    return linkcode_resolve


def build_config(
        package, config_file, project,
        author=None,
        author_name=None,
        github_project=None,
        webdomain=None,
        canonical_url=None,
        canonical_stable_url=None,
        canonical_dev_url=None,
        django_settings=None,
        configure_django_settings={},
        copyright=None,
        publisher=None,
        description='',
        path_additions=['_ext'],
        version_dev=None,
        version_stable=None,
        extensions=EXTENSIONS,
        extra_extensions=[],
        linkcode_url=LINKCODE_URL,
        github_branch=GITHUB_BRANCH,
        master_doc='index',
        html_logo=None,
        html_prepend_sidebars=[],
        templates_path=None,
        latex_logo=None,
        intersphinx_mapping=INTERSPHINX_MAPPING,
        extra_intersphinx_mapping={},
        include_intersphinx=frozenset(),
        exclude_intersphinx=frozenset(),
        spelling_lang='en_US',
        spelling_show_suggestions=True,
        extlinks=None,
        **kwargs):
    add_paths(config_file, path_additions)
    if configure_django_settings or django_settings:
        configure_django(django_settings, **configure_django_settings or {})
    package = import_package(package)
    description = description or package.__doc__
    author = author or package.__author__
    author_name = author_name or author
    extlinks = extlinks or {}

    extlinks.setdefault('sha', (
        'https://github.com/{0}/commit/%s'.format(github_project),
        'GitHub SHA@',
    ))
    extlinks.setdefault('github_branch', (
        'https://github.com/{0}/tree/%s'.format(github_project),
        'GitHub branch',
    ))
    extlinks.setdefault('github_user', (
        'https://github.com/%s/', '@',
    ))
    extlinks.setdefault('pypi', (
        'https://pypi.python.org/pypi/%s/', '',
    ))
    extlinks.setdefault('wikipedia', (
        'https://en.wikipedia.org/wiki/%s', '',
    ))

    if not canonical_dev_url:
        canonical_dev_url = '/'.join([
            canonical_url.rstrip('/'), 'en', 'master',
        ])
    if not canonical_stable_url:
        canonical_stable_url = '/'.join([
            canonical_url.rstrip('/'), 'en', 'latest',
        ])

    if templates_path is None:
        templates_path = ['_templates']
    if version_dev:
        templates_path.append(get_html_templates_path())

    version = '.'.join(map(str, package.VERSION[0:2]))

    extensions = extensions + extra_extensions
    if os.environ.get('SPELLCHECK'):
        extensions.append('sphinxcontrib.spelling')

    conf = dict(
        extensions=extensions + extra_extensions,

        project=project,
        github_project=github_project,

        html_show_sphinx=False,

        # Add any paths that contain templates here,
        #   relative to this directory.
        templates_path=templates_path,

        # The suffix of source filenames.
        source_suffix='.rst',

        # The master toctree document.
        master_doc=master_doc,

        copyright='{0}, {1}'.format(copyright, author),

        # The short X.Y version.
        version=version,

        # The full version, including alpha/beta/rc tags.
        release=package.__version__,

        exclude_patterns=['_build', 'Thumbs.db', '.DS_Store'],

        # If true, '()' will be appended to :func: etc. cross-reference text.
        add_function_parentheses=True,

        linkcode_resolve=create_linkcode_resolver(
            linkcode_url, github_project, github_branch,
        ),

        intersphinx_mapping=prepare_intersphinx_mapping(
            project,
            intersphinx_mapping,
            include_intersphinx,
            exclude_intersphinx,
            **extra_intersphinx_mapping
        ),

        # The name of the Pygments (syntax highlighting) style to use.
        pygments_style='colorful',

        # Add any paths that contain custom static files
        # (such as style sheets) here, relative to this directory.
        # They are copied after the builtin static files, so a file named
        # "default.css" will overwrite the builtin "default.css".
        html_static_path=['_static'],

        add_module_names=True,
        highlight_language='python3',

        # If true, `todo` and `todoList` produce output,
        # else they produce nothing.
        todo_include_todos=True,

        # If false, no module index is generated.
        html_use_modindex=True,

        # If false, no index is generated.
        html_use_index=True,

        html_logo=html_logo,

        html_context={
            'version_dev': version_dev or version,
            'version_stable': version_stable or version,
            'canonical_stable_url': canonical_stable_url,
            'canonical_dev_url': canonical_dev_url,
        },

        man_pages=[
            (master_doc, project.lower(),
             u'{0} Documentation'.format(project), [author_name], 1)
        ],

        # Grouping the document tree into Texinfo files. List of tuples
        # (source start file, target name, title, author,
        #  dir menu entry, description, category)
        texinfo_documents=[
            (master_doc, project, u'{0} Documentation'.format(project),
             author_name, project, description,
             'Miscellaneous'),
        ],
        latex_logo=latex_logo or html_logo,

        latex_documents=[
            ('index', '{0}.tex'.format(project),
             '{0} Documentation'.format(project), author, 'manual'),
        ],
        html_theme='sphinx_celery',
        html_sidebars={
            'index': list(html_prepend_sidebars) + [
                'sourcelink.html',
                'searchbox.html',
            ],
            '**': list(html_prepend_sidebars) + [
                'relations.html',
                'sourcelink.html',
                'searchbox.html',
            ],
        },
        # Bibliographic Dublin Core info.
        epub_title='{0} Manual, Version {1}'.format(project, version),
        epub_author=author_name,
        epub_publisher=publisher or author_name,
        epub_copyright=copyright,

        # The language of the text. It defaults to the language option
        # or en if the language is not set.
        epub_language='en',

        # The scheme of the identifier. Typical schemes are ISBN or URL.
        epub_scheme='ISBN',

        # The unique identifier of the text. This can be a ISBN number
        # or the project homepage.
        epub_identifier=webdomain,

        # A unique identification for the text.
        epub_uid='{0} Manual, Version {0}'.format(project, version),

        # A list of files that should not be packed into the epub file.
        epub_exclude_files=['search.html'],

        # The depth of the table of contents in toc.ncx.
        epub_tocdepth=3,

        # -- spelling
        spelling_lang=spelling_lang,
        spelling_show_suggestions=spelling_show_suggestions,

        # -- extlinks
        extlinks=extlinks,
    )
    return dict(conf, **kwargs)
