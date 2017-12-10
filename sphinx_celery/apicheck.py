"""

Sphinx Autodoc coverage checker.
================================

This builder extension makes sure all modules in the documented
package is represented in the autodoc API reference.

Usage
-----

.. code-block:: console

    $ sphinx-build -b apicheck -d _build/doctrees . _build/apicheck

Configuration
-------------

apicheck_ignore_modules
~~~~~~~~~~~~~~~~~~~~~~~

List of modules to ignore, either as module names or regexes.

Example:

.. code-block:: python

    apicheck_ignore_modules = [
        'django.utils.functional',
        r'django.db.*',
    ]

Test packages are ignored by default, even if this setting is defined.

apicheck_package
~~~~~~~~~~~~~~~~

The package to verify, can be the fully-qualified name of a module
or an actual module.

Example:

.. code-block:: python

    apicheck_package = 'django'

Default is the value of the ``project`` configuration key in all lowercase.


apicheck_domains
~~~~~~~~~~~~~~~~

List of domains to check.

Default is ``['py']`` and Python is the only domain currently supported.

"""
from __future__ import absolute_import, unicode_literals

import importlib
import os

from collections import defaultdict
from six import string_types

from sphinx.ext import autodoc
from sphinx.util.console import bold, darkgreen, green, red

from .builders import BaseBuilder
from .utils import bytes_if_py2

DEFAULT_IGNORE = [r'.*?\.tests.*']

TITLEHEADER = '='
SUBHEADER = '-'

ERR = 'ERROR'
ERR_MISSING = '{error}: In index but module does not exist: {module}'
ERR_UNDOCUMENTED = 'Undocumented Autodoc Modules'
OK_STATUS = 'OK: All modules documented :o)'

NOK_STATUS = """
{title}

{undocumented}\
"""

DOMAIN_FORMAT = """\
{domain}

{modules}
"""

MODULE_FORMAT = '- {module}'


class ModuleDocumenter(autodoc.ModuleDocumenter):
    missing_modules = set()

    def import_object(self):
        if not super(ModuleDocumenter, self).import_object():
            self.missing_modules.add(self.modname)
            return False
        return True


def title(s, spacing=2, sep=TITLEHEADER):
    return '\n'.join([
        sep * (len(s) + spacing),
        '{0}{1}{0}'.format(' ' * (spacing // 2), red(s)),
        sep * (len(s) + spacing),
    ])


def header(s, sep=SUBHEADER):
    return '\n'.join([bold(s), sep * len(s)])


def find_python_modules(package):
    if isinstance(package, string_types):
        package = importlib.import_module(package)
    name, path = package.__name__, package.__file__
    current_dist_depth = len(name.split('.')) - 1
    current_dist = os.path.join(os.path.dirname(path),
                                *([os.pardir] * current_dist_depth))
    abs = os.path.abspath(current_dist)
    dist_name = os.path.basename(abs)

    for dirpath, dirnames, filenames in os.walk(abs):
        package = (dist_name + dirpath[len(abs):]).replace('/', '.')
        if '__init__.py' in filenames:
            yield package
            for filename in filenames:
                if filename.endswith('.py') and filename != '__init__.py':
                    yield '.'.join([package, filename])[:-3]


class APICheckBuilder(BaseBuilder):

    name = 'apicheck'
    pickle_filename = 'apicheck.pickle'

    find_modules = {
        'py': find_python_modules,
    }

    def init(self):
        self.ignore_patterns = self.compile_regexes(
            self.config.apicheck_ignore_modules + DEFAULT_IGNORE,
        )
        self.check_domains = self.config.apicheck_domains
        self.check_package = (
            self.config.apicheck_package or self.config.project.lower())

        self.undocumented = defaultdict(list)
        self.all_modules = defaultdict(set)

    def is_ignored_module(self, module):
        return any(regex.match(module) for regex in self.ignore_patterns)

    def write(self, *ignored):
        for domain in self.check_domains:
            self.build_coverage(domain)
        self.check_missing()
        if not self.app.statuscode:
            self.write_coverage(self.check_domains)

    def build_coverage(self, domain):
        self.all_modules[domain].update(self.find_modules[domain](
            self.check_package,
        ))
        self.undocumented[domain].extend(self.find_undocumented(
            domain, self.env.domaindata[domain]['modules'],
        ))

    def find_undocumented(self, domain, documented):
        return (
            mod for mod in self.all_modules[domain]
            if mod not in documented and not self.is_ignored_module(mod)
        )

    def write_coverage(self, domains):
        status = any(self.undocumented.values())
        if status:
            self.app.statuscode = 2
            print(self.format_undocumented_domains(domains))
        else:
            print(green(OK_STATUS))

    def check_missing(self):
        for mod in ModuleDocumenter.missing_modules:
            self.app.statuscode = 3
            print(ERR_MISSING.format(
                error=red(ERR),
                module=bold(mod),
            ))

    def format_undocumented_domains(self, domains):
        return NOK_STATUS.format(
            title=title(ERR_UNDOCUMENTED),
            undocumented='\n'.join(
                self.format_undocumented_domain(domain) for domain in domains
            ),
        )

    def format_undocumented_domain(self, domain):
        return DOMAIN_FORMAT.format(domain=header(domain), modules='\n'.join(
            self.format_undocumented_module(module)
            for module in self.undocumented[domain]
        ))

    def format_undocumented_module(self, module):
        return MODULE_FORMAT.format(module=darkgreen(module))

    def as_dict(self):
        return {
            'undocumented': dict(self.undocumented),
        }


def setup(app):
    app.add_builder(APICheckBuilder)
    app.add_config_value(
        bytes_if_py2('apicheck_ignore_modules'), [], False)
    app.add_config_value(
        bytes_if_py2('apicheck_domains'), ['py'], False)
    app.add_config_value(
        bytes_if_py2('apicheck_package'), None, False)
    reg = autodoc.AutoDirective._registry
    reg[ModuleDocumenter.objtype] = ModuleDocumenter


    return {
        'parallel_read_safe': True
    }
