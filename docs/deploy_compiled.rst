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


``compiledir``
    This is the directory we will save all the output.  The value of
    ``compiledir`` should be a string representing the **absolute
    path** of the output directory for compiling.

    For example, Joe puts the output in his ``public_html`` directory
    of his account:

    .. code-block:: python

       py["compiledir"] = "/home/joe/public_html"


``base_url``
    Set ``base_url`` in your ``config.py`` file to the base url your
    blog will have.

    For example, if your ``compiledir`` were set to
    ``/home/joe/public_html`` and the url for that directory were
    ``http://example.com/~joe/``, then you probably want to set your
    base_url like this:

    .. code-block:: python

       py["base_url"] = "http://example.com/~joe/"


``compile_themes`` (Optional)
    Defaults to ``['html']``.

    The value of ``compile_themes`` should be a list of strings
    representing all the themes that should be rendered.

    For example:

    .. code-block:: python

       py["compile_themes"] = ["html"]


``compile_index_themes`` (Optional)
    Defaults to ``["html"]``.

    ``compile_index_themes`` is just like ``compile_themes`` except
    it's the themes of the index files: frontpage index, category
    indexes, date indexes, ...

    Defaults to ``["html"]`` which only renders the html theme.

    For example:

    .. code-block:: python

       py["compile_index_themes"] = ["html"]


    If you want your index files to also be feeds, then you should add
    a feed theme to the list.


``compile_day_indexes`` (Optional)
    Defaults to ``False``.

    Whether or not to generate indexes per day.

    For example:

    .. code-block:: python

       py["compile_day_indexes"] = True


``compile_month_indexes`` (Optional)
    Defaults to ``False``.

    Whether or not to generate indexes per day.

    For example:

    .. code-block:: python

       py["compile_month_indexes"] = True


``compile_urls`` (Optional)
    Any other url paths to compile.  Sometimes plugins require you to
    add additional paths---this is where you'd do it.

    For example:

    .. code-block:: python

       py["compile_urls"] = [
           "/booklist"
       ]


Configuring collectstatic
=========================

``static_url``
    The full url for your static assets.

    If you're using a CDN, this is the CDN url.

    If you're not using a CDN, this is probably the base_url plus
    ``/static``.

    You can use this variable in your templates. For example:

    .. code-block:: html

       <link rel="stylesheet" href="{{ static_url }}/css/style.css">


``static_files_dirs`` (Optional)
    Any additional directories you want copied over to the compiledir.

    For example:

    .. code-block:: python

       py['static_files_dirs'] = [
           '/home/joe/blog/staticimages/',
           '/home/joe/blog/blogimages/'
       ]


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
