============
Contributing
============

This covers the basics you need to know for contributing to
Douglas.

.. contents::
   :local:


Status
======

**December 27th, 2013**

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

Clone the project using git:

.. code-block:: bash

   $ git clone https://github.com/willkg/douglas.git

Set ``user.name`` and ``user.email`` git configuration:

.. code-block:: bash

   $ git config user.name "your name"
   $ git config user.email "your@email.address"

Create a new branch off of master for any new work that you do.

When you want to send it upstream, do:

.. code-block:: bash

   $ git format-patch --stdout origin/master > NAME_OF_PATCH_FILE.patch

where ``NAME_OF_PATCH_FILE`` is a nice name that's short and
descriptive of what the patch holds and master should be replaced with your
branch name

Then attach that ``.patch`` file and send it to douglas-devel
mailing list.


Installing for hacking
======================

1. Clone the project into a directory
2. Create a virtual environment and activate it
3. Install Douglas into your virtual environment in a way that's suitable for hacking:

   .. code-block:: bash

      $ pip install -e .

4. Install development requirements:

   .. code-block:: bash

      $ pip install -r requirements-dev.txt


Create a new blog:

.. code-block:: bash

   $ douglas-cmd create [<dir>]

Generate "sample" entries:

.. code-block:: bash

   $ douglas-cmd generate [<num_entries>]

Douglas comes with


Code conventions
================

Follow `PEP-8 <http://www.python.org/dev/peps/pep-0008/>`_.

Best to run pyflakes and pep8 over your code.

Don't use l as a variable name.


Tests
=====

In the douglas git repository, there are two big things that have
test suites:

1. the Douglas core code
2. the plugins that are in ``douglas/plugins/``

Please add tests for changes you make. In general, it's best to write
a test, verify that it fails, then fix the code which should make the
test pass.

Tests go in ``douglas/tests/``.

We use `nose <https://nose.readthedocs.io/>`_ because it's
super.

Run the tests by:

.. code-block:: bash

   $ nosetests


The ``douglas.tests`` package defines helper functions, classes, and
other things to make testing easier.

Writing tests is pretty easy:

1. create a file in ``douglas/tests/`` with a filename that starts
   with ``test_`` and ends with ``.py``.

2. at the top, do:

   .. code-block:: python

      from douglas.tests import UnitTestBase


3. create a subclass of ``UnitTestBase``

4. write some tests using pretty standard unittest/nose stuff

See ``douglas/tests/`` for examples testing the core as well as core
plugins.


Documentation
=============

New features should come with appropriate changes to the documentation.

Documentation is in the ``docs/`` directory, written using
`reStructuredText <http://docutils.sourceforge.net/rst.html>`_, and
built with `Sphinx <http://sphinx.pocoo.org/>`_.
