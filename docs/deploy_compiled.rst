.. _compiling:

======================================
Deploy Douglas as a Compiled HTML Site
======================================

.. contents::
   :local:


Summary
=======

Compiling your blog to static HTML allows you to generate your blog
and push it via scp or ftp to host most anywhere.  If your blog isn't
interactive or you need to host your blog on a system that doesn't let
you run a CGI script or a WSGI app, then this is the easiest way to do
it.

Compiling your blog happens in two steps:

1. ``douglas-cmd compile``
2. ``douglas-cmd collectstatic``

After that, you'll have a single directory with the compiled form of
your blog. You can scp, ftp, rsync, unison or whatever this directory
to the host for serving.


Configuring compiling
=====================

To compile your blog, you need to set the ``compiledir`` setting in
your ``config.py`` file.  That tells Douglas which directory to
compile your blog to.  Everything else is optional and has defaults.

:py:data:`base_url <douglas.settings.Config.base_url>`
   For example, if your ``compiledir`` were set to
   ``/home/joe/public_html`` and the url for that directory were
   ``http://example.com/~joe/``, then you probably want to set your
   base_url like this:

   .. code-block:: python

      py["base_url"] = "http://example.com/~joe"

:py:data:`compiledir <douglas.settings.Config.compiledir>`
   The directory to compile your blog into.

:py:data:`compile_themes <douglas.settings.Config.compile_themes>`
   The themes to compile all pages in.

:py:data:`compile_index_themes <douglas.settings.Config.compile_index_themes>`
   The themes to compile index pages in.

:py:data:`day_indexes <douglas.settings.Config.day_indexes>`
   Whether or not to do day-based indexes.

:py:data:`month_indexes <douglas.settings.Config.month_indexes>`
   Whether or not to do month-based indexes.

:py:data:`year_indexes <douglas.settings.Config.year_indexes>`
   Whether or not to do year-based indexes.

:py:data:`compile_urls <douglas.settings.Config.compile_urls>`
   List of additional urls to compile.


Configuring collectstatic
=========================

:py:data:`static_url <douglas.settings.Config.static_url>`
   The url where your static assets will be. If you're using a CDN, then this
   will be a complete url. Otherwise you probably want to set this to your
   :py:data:`base_url <douglas.settings.Config.base_url>` plus ``/static``.

:py:data:`static_files_dir <douglas.settings.Config.static_files_dir>`
   The list of additional directories to copy static assets from.


Compiling your blog
===================

To compile your blog, ``cd`` into your blog's directory and run:

.. code-block:: bash

   $ douglas-cmd compile


After that, collect the static files:

.. code-block:: bash

   $ douglas-cmd collectstatic


Once you've done both of those steps, you can copy the compiledir to
your blog host.

See:

.. code-block:: bash

   $ douglas-cmd compile --help


and:

.. code-block:: bash

   $ douglas-cmd collectstatic --help


for options.


Example setup
=============

I keep my blog on my server in ``/home/will/blog``.  I compile it to
my ``/home/will/public_html`` directory.

My directory layout looks like::

   /home/will
      blog/
        |- static/
        |  |- images/
        |  |- css/
        |  \- js/
        |
        |- entries/       # all my blog entries
        |- themes/        # themes and templates
        |- plugins/       # a couple of plugins I use
        |
        |- config.py      # my config.py file
        |- compile.sh     # shell script below


Here's the relevant portions of my ``config.py`` file:

.. code-block:: python

   py["base_url"] = "http://example.com/~joe/blog"

   py["compiledir"] = "/home/will/public_html/blog/"
   py["compile_themes"] = ["html"]
   py["compile_index_themes"] = ["html", "atom"]
   py["compile_day_indexes"] = False
   py["compile_month_indexes"] = False
   py["compile_year_indexes"] = True

   py["static_url"] = "http://example.com/~joe/blog/static"
   py["static_files_dirs"] = []


My compile.sh file looks like this:

.. code-block:: bash

   #!/bin/bash

   BLOGDIR=/home/will/blog
   OUTPUTDIR=/home/will/public_html/blog

   # compile entire blog
   douglas-cmd compile --config ${BLOGDIR}

   # copy static assets
   douglas-cmd collectstatic --config ${BLOGDIR}


Troubleshooting
===============

Can't find config.py file
-------------------------

Use the ``--config <path/to/config.py/file>`` argument.


There are all these old files in my compiledir
----------------------------------------------

Both compiling everything and compiling incrementally *won't* remove
outdated files. If you want old files removed, you should delete the
directory, then compile and collect static files.


OMG! I don't want an RSS version of every page in my blog!
----------------------------------------------------------

You probably don't want to compile an RSS or Atom version of every
blog entry, so don't include those themes in ``compile_themes`` and
instead specify the themes you want for index pages in
``compile_index_themes`` or the specific urls you want in
``compile_urls``.


I want to use a CSS compiler, JS minifier, etc
----------------------------------------------

Put your CSS/JS source files in your static directories, then compile
them into their CSS/JS forms and then run:

.. code-block:: bash

   $ douglas-cmd collectstatic
