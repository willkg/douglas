============
Contributing
============

This covers the basics you need to know for contributing to
Douglas.


Status
======

I'm rewriting Pyblosxom fixing a lot of problems I had with it. This
project is in crazy flux right now. I don't expect anyone to want to
help at this stage. If you want to help anyways, see the issues in
the issue tracker for what's in the queue of things to fix.


How to clone the project
========================

`Douglas is on GitHub <https://github.com/willkg/douglas>`_.


If you have a GitHub account [Recommended]
-------------------------------------------

This is the ideal way to contribute because GitHub makes things simple
and convenient.

Go to the project page (https://github.com/willkg/douglas) and click on
"Fork" at the top right on the screen. GitHub will create a copy of the 
Douglas repository in your account for you to work on.

Create a new branch off of master for any new work that you do.

When you want to send it upstream, create a pull request.

If you need help with this process, `see the GitHub documentation
<http://help.github.com/>`_.


If you don't have a GitHub account
----------------------------------

Clone the project using git::

    git clone https://github.com/willkg/douglas.git

Set ``user.name`` and ``user.email`` git configuration::

    git config user.name "your name"
    git config user.email "your@email.address"

Create a new branch off of master for any new work that you do.

When you want to send it upstream, do::

    git format-patch --stdout origin/master > NAME_OF_PATCH_FILE.patch

where ``NAME_OF_PATCH_FILE`` is a nice name that's short and
descriptive of what the patch holds and master should be replaced with your 
branch name

Then attach that ``.patch`` file and send it to douglas-devel
mailing list.


Code conventions
================

Follow `PEP-8 <http://www.python.org/dev/peps/pep-0008/>`_.

Best to run pyflakes and pep8 over your code.

Don't use l as a variable name.


Tests
=====

Please add tests for changes you make. In general, it's best to write
a test, verify that it fails, then fix the code which should make the
test pass.

Tests go in ``douglas/tests/``.

Tests are run with `nose <https://nose.readthedocs.org/en/latest/>`_.


Documentation
=============

New features should come with appropriate changes to the documentation.

Documentation is in the ``docs/`` directory, written using
`reStructuredText <http://docutils.sourceforge.net/rst.html>`_, and
built with `Sphinx <http://sphinx.pocoo.org/>`_.
