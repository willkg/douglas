.. _hacking-chapter:

==================
Hacking on Douglas
==================

This will cover installing Douglas from the git repositories in a
way that won't interfere with the packages or modules already installed on 
the system.

Installing Douglas to hack on it is a little different since you:

1. want to be running Douglas from a git clone

2. want Douglas installed such that you don't have to keep running
   ``python setup.py install``

3. want Paste installed so you can test locally


As such, this document covers installing Douglas into a virtual environment 
and deploying it using Paste.


Requirements
============

This requires:

* Python 2.7
* `git`_
* `virtualenv`_
* `PasteScript`_, the command-line frontend for the Python Paste web
  development utilities

.. _git: http://git-scm.com/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _PasteScript: http://pypi.python.org/pypi/PasteScript


Installation
============

To install:

1. Create a virtual environment for Douglas into a directory of your
   choosing as denoted by ``<VIRTUAL-ENV-DIR>``::

       virtualenv <VIRTUAL-ENV-DIR>

   Or use virtualenvwrapper---that's usually way easier::

       mkvirtualenv douglas


   This is the virtual environment that Douglas will run in.  If you
   decide to delete Douglas at some point, you can just remove this
   virtual environment directory.


2. Activate the virtual environment::

       source <VIRTUAL-ENV-DIR>/bin/activate

   Or if you used virtualenvwrapper::

       workon douglas

   Remember to activate the virtual environment **every** time you do
   something with Douglas.

   Additionally, if you're running Douglas from CGI or a cron job,
   you want to use the ``python`` interpreter located in the ``bin``
   directory of your virtual environment--not the system one.

3. Using git, clone the Douglas repository::

      git clone https://github.com/douglas/douglas.git

4. Change directories into the ``douglas`` directory and run::

      pip install -r requirements-dev.txt


Running Douglas
===============

When you want to run Douglas from your git clone in your virtual
environment, you will:

1. Make sure the virtual environment is activated and if it isn't do::

       source <VIRTUAL-ENV-DIR>/bin/activate

   Or::

       workon douglas

2. Change directories into where you have your blog and do::

      paster serve blog.ini

	  
Updating Douglas
================

If you followed the instructions above, then it should just continue to work
unless the version has changed. In that case, just do::

    pip install -r requirements-dev.txt

again.
