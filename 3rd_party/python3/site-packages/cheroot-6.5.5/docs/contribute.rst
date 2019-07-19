.. include:: ../.github/CONTRIBUTING.rst


First-time setup
~~~~~~~~~~~~~~~~

- You need to install `Python`_ 3 which is required for building docs.
For example, Python 3.7.

Then, `create and activate a virtual environment`_.
And install `tox`_.

- `Install git`_

- `Configure git`_:

1. Please, identify yourself::

    $ git config --global user.name "firstname lastname"
    $ git config --global user.email yourname@example.com

* Use the address bound to your GitHub account so that the commits would be linked to your profile.

2. Choose an editor for Git::

    $ git config --global core.editor vim

- Create and log in to a `GitHub`_ account

- `Fork`_ Cheroot to your GitHub account by clicking the Fork button

- `Clone`_ your fork locally::

    $ git clone https://github.com/{username}/cheroot
    $ cd cheroot

* Also, you can `clone`_ fork using `ssh`_::

    $ git clone git@github.com:{username}/cheroot.git
    $ cd cheroot

- To create a new `branch`_ and switch to it::

    $ git checkout -b patch/some_fix

.. _create and activate a virtual environment: https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments
.. _Python: https://www.python.org/
.. _Install git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _Configure git: https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup
.. _GitHub: http://github.com
.. _Fork: https://help.github.com/articles/fork-a-repo/
.. _Clone: https://help.github.com/articles/cloning-a-repository/
.. _ssh: https://help.github.com/articles/connecting-to-github-with-ssh/
.. _branch: https://www.atlassian.com/git/tutorials/using-branches

Write your code
~~~~~~~~~~~~~~~

- Please, use `PEP 8`_

.. _PEP 8: https://pep8.org/

Once you finished coding, you are recommended to do the following steps:
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

- Run tests with `tox`_

Run one test with Python3.6::

    $ tox -e py36 -- cheroot/test/test_name.py

**`tox`** — Run all tests using the Python version where `python` command
currently points to which is specified in tox settings::

    envlist = python
    minversion = 3.5.3

Run linters and all tests against several Python interpreters::

    $ tox -e pre-commit,py27,py37  # etc.

- Run the `pre-commit`_ linting suite::

    $ tox -e pre-commit

- `git add`_ your files

- `Write good`_ `commit messages`_ when checking in your changes to Git

- `Push`_ and `create a pull request`_

.. _tox: https://tox.readthedocs.io/en/latest/
.. _pre-commit: https://github.com/pre-commit/pre-commit
.. _git add: https://git-scm.com/docs/git-add
.. _Write good: https://chris.beams.io/posts/git-commit/
.. _commit messages: https://git-scm.com/docs/git-commit
.. _Push: https://git-scm.com/docs/git-push
.. _create a pull request: https://help.github.com/articles/creating-a-pull-request/

Building the docs
~~~~~~~~~~~~~~~~~

To build the docs from a checked out source, run::

    $ tox -e build-docs

Open the documentation:

.. tabs::

   .. tab:: GNU/linux

      $ xdg-open build/html/index.html

   .. tab:: macOS

      $ open build/html/index.html

   .. tab:: Windows

      Please, open build/html/index.html in your browser.

Also, one can serve docs using a built-in static files server.
This is preferable because of possible CSRF issues.::

    $ python3 -m http.server --directory build/html/ 8000

After that, you can open `http://localhost:8000/ <http://localhost:8000/>`_ in your browser.

Read more about `Sphinx`_.

.. _Sphinx: https://www.sphinx-doc.org
