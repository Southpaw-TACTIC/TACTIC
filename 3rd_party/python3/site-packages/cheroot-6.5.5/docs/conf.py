#!/usr/bin/env python3
# Requires Python 3.6+
"""Configuration of Sphinx documentation generator."""

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'jaraco.packaging.sphinx',
    'rst.linker',
    'sphinx_tabs.tabs',
]

master_doc = 'index'

link_files = {
    '../CHANGES.rst': dict(
        replace=[
            dict(
                pattern=r'^(?m)((?P<scm_version>v?\d+(\.\d+){1,2}))\n[-=]+\n',
                with_scm='{text}\n{rev[timestamp]:%d %b %Y}\n',
            ),
        ],
    ),
}

github_url = 'https://github.com'
github_repo_org = 'cherrypy'
github_repo_name = 'cheroot'
github_repo_slug = f'{github_repo_org}/{github_repo_name}'
github_repo_url = f'{github_url}/{github_repo_slug}'
cp_github_repo_url = f'{github_url}/{github_repo_org}/cherrypy'

extlinks = {
    'issue': (f'{github_repo_url}/issues/%s', '#'),
    'pr': (f'{github_repo_url}/pull/%s', 'PR #'),
    'commit': (f'{github_repo_url}/commit/%s', ''),
    'cp-issue': (f'{cp_github_repo_url}/issues/%s', 'CherryPy #'),
    'cp-pr': (f'{cp_github_repo_url}/pull/%s', 'CherryPy PR #'),
    'gh': (f'{github_url}/%s', 'GitHub: '),
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'python2': ('https://docs.python.org/2', None),
    'cherrypy': ('https://docs.cherrypy.org/en/latest/', None),
    'trustme': ('https://trustme.readthedocs.io/en/latest/', None),
}
