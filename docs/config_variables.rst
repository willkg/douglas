===================
Configuring Douglas
===================

You configure a Douglas blog by setting configuration variables in a
Python file called ``config.py``.  Each Douglas blog has its own
``config.py`` file.

This chapter documents the ``config.py`` variables.  Some of these are
required, others are optional.

.. Note::

   Douglas comes with a sample config file.  This file does **not**
   have everything listed below in it.  If you want to use a variable
   that's not listed in your config file---just add it.


Config variables and syntax
===========================

Each configuration variable is set with a line like:


.. code-block:: python

   py["blog_title"] = "Another douglas blog"


where:

* ``blog_title`` is the name of the configuration variable
* ``"Another douglas blog"`` is the value

Most configuration values are strings and must be enclosed in quotes,
but some are lists, numbers or other types of values.

Examples:

.. code-block:: python

   # this has a string value
   py["foo"] = "this is a string"

   # this is a long string value
   py["foo"] = (
       "This is a really long string value that breaks over "
       "multiple lines.  The parentheses cause Python to "
       "allow this string to span several lines."
   )

   # this has an integer value
   py["foo"] = 4

   # this is a boolean--True has a capital T
   py["foo"] = True

   # this is a boolean--False has a capital F
   py["foo"] = False

   # this is a list of strings
   py["foo"] = [
       "list",
       "of",
       "strings"
   ]

   # this is the same list of strings formatted slightly differently
   py["foo"] = ["list", "of", "strings"]


Since ``config.py`` is a Python code file, it's written in Python and
uses Python code conventions.


Plugin variables
================

If you install any Douglas plugins those plugins may ask you to set
additional variables in your ``config.py`` file.  Those variables will
be documented in the documentation that comes with the plugin or at
the top of the plugin's source code file.  Additional plugin variables
will not be documented here.


Personal configuration variables
================================

You can add your own personal configuration variables to
``config.py``.  You can put any ``py["name"] = value`` statements that
you want in ``config.py``.  You can then refer to your configuration
variables further down in your ``config.py`` file and in your theme
templates.  This is useful for allowing you to centralize any
configuration for your blog into your ``config.py`` file.

For example, you could move all your media files (JPEG images, GIF
images, CSS, ...) into a directory on your server to be served by
Apache and then set the config.py variable ``py["media_url"]`` to the
directory with media files and use ``$media_url`` to refer to this URL
in your theme templates.


.. _configuration-variables:

Configuration variables
=======================

.. autoclass:: douglas.settings.Config
   :members:


Compiling Configuration
=======================

If you are using compiling to deploy your Douglas blog you
need to set some additional configuration variables in your
``config.py`` file, see :ref:`compiling`.
