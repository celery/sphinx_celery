import os
import sys

from . import get_html_templates_path

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
    'python': ('https://docs.python.org/dev/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/stable/', None),
    'kombu': ('https://kombu.readthedocs.io/en/main/', None),
    'celery': ('https://celery.readthedocs.io/en/main/', None),
    'pytest-celery': ('https://pytest-celery.readthedocs.io/en/main/', None),
    'djcelery': ('https://django-celery.readthedocs.io/en/latest/', None),
    'cyme': ('https://cyme.readthedocs.io/en/latest/', None),
    'amqp': ('https://amqp.readthedocs.io/en/latest/', None),
    'vine': ('https://vine.readthedocs.io/en/latest/', None),
    'flower': ('https://flower.readthedocs.io/en/latest/', None),
    'redis': ('https://redis-py.readthedocs.io/en/latest/', None),
    'django': (
        'http://docs.djangoproject.com/en/dev/',
        'https://docs.djangoproject.com/en/dev/_objects',
    ),
    'boto': ('https://boto.readthedocs.io/en/latest/', None),
    'sqlalchemy': ('https://sqlalchemy.readthedocs.io/en/latest', None),
    'kazoo': ('https://kazoo.readthedocs.io/en/latest/', None),
    'msgpack': ('https://msgpack-python.readthedocs.io/en/latest/', None),
    'riak': ('https://basho.github.io/riak-python-client/', None),
    'pylibmc': ('http://sendapatch.se/projects/pylibmc/', None),
    'eventlet': ('https://eventlet.net/doc/', None),
    'gevent': ('http://www.gevent.org/', None),
    'pyOpenSSL': ('https://pyopenssl.readthedocs.io/en/stable/', None),
    'pytest': ('https://docs.pytest.org/en/latest/', None),
    'tox': ('https://tox.readthedocs.io/en/latest', None),
}


def add_paths(config_file, path_additions):
    this = os.path.dirname(os.path.abspath(config_file))

    sys.path.insert(0, os.path.join(this, os.pardir))
    for path in path_additions:
        sys.path.append(os.path.join(this, path))


def configure_django(django_settings, **config):
    if django_settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings
    else:
        from django.conf import settings
        if not settings.configured:
            settings.configure(**config)
    try:
        from django import setup as django_setup
    except ImportError:
        pass
    else:
        django_setup()


def import_package(package):
    if isinstance(package, str):
        return __import__(package)
    return package


def prepare_intersphinx_mapping(project, mapping,
                                include, exclude, **extra):
    if include:
        mapping = {k: v for k, v in mapping.items() if k in include}
    if exclude:
        mapping = {k: v for k, v in mapping.items() if k not in exclude}
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
        f'https://github.com/{github_project}/commit/%s',
        'GitHub SHA@%s',
    ))
    extlinks.setdefault('github_branch', (
        f'https://github.com/{github_project}/tree/%s',
        'GitHub branch %s',
    ))
    extlinks.setdefault('github_user', (
        'https://github.com/%s/', '@%s',
    ))
    extlinks.setdefault('pypi', (
        'https://pypi.org/project/%s/', None,
    ))
    extlinks.setdefault('wikipedia', (
        'https://en.wikipedia.org/wiki/%s', None,
    ))

    if not canonical_dev_url:
        canonical_dev_url = '/'.join([
            canonical_url.rstrip('/'), 'en', 'main',
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

        copyright=f'{copyright}, {author}',

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
             f'{project} Documentation', [author_name], 1)
        ],

        # Grouping the document tree into Texinfo files. List of tuples
        # (source start file, target name, title, author,
        #  dir menu entry, description, category)
        texinfo_documents=[
            (master_doc, project, f'{project} Documentation',
             author_name, project, description,
             'Miscellaneous'),
        ],
        latex_logo=latex_logo or html_logo,

        latex_documents=[
            ('index', f'{project}.tex',
             f'{project} Documentation', author, 'manual'),
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
        epub_title=f'{project} Manual, Version {version}',
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
        epub_uid=f"{project} Manual, Version {version}",

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
