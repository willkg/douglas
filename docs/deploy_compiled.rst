.. _compiling:

======================================
Deploy Douglas as a Compiled HTML Site
======================================

Summary
=======

Compiling your blog to static HTML allows you to generate your blog
and push it via scp or ftp to host most anywhere.  If your blog isn't
interactive, then this is the easiest way to do it.

Douglas's compiling system also allows for incremental building.  It
can scan your entries, figure out what's changed, and compiles only the
pages that need re-compiling.


Configuring compiling
=====================

To compile your blog, you need to set the ``compiledir`` setting in your
``config.py`` file.  That tells Douglas which directory to compile your
blog to.  Everything else is optional and has defaults.


``compiledir``
    This is the directory we will save all the output.  The value of 
    ``compiledir`` should be a string representing the **absolute path** of the 
    output directory for compiling.

    For example, Joe puts the output in his ``public_html`` directory of his
    account::

        py["compiledir"] = "/home/joe/public_html"


``base_url``
    Set ``base_url`` in your ``config.py`` file to the base url your 
    blog will have.

    For example, if your ``compiledir`` were set to
    ``/home/joe/public_html`` and the url for that directory were
    ``http://example.com/~joe/``, then you probably want to set your
    base_url like this::

        py["base_url"] = "http://example.com/~joe/"


``compile_themes`` (Optional)
    Defaults to ``['html']``.

    The value of ``compile_themes`` should be a list of strings representing 
    all the themes that should be rendered.

    For example::

        py["compile_themes"] = ["html"]


``compile_index_themes`` (Optional)
    Defaults to ``["html"]``.

    ``compile_index_themes`` is just like ``compile_themes`` except
    it's the themes of the index files: frontpage index, category
    indexes, date indexes, ...

    Defaults to ``["html"]`` which only renders the html theme.

    For example::

        py["compile_index_themes"] = ["html"]

    If you want your index files to also be feeds, then you should add
    a feed theme to the list.


``compile_day_indexes`` (Optional)
    Defaults to ``False``.

    Whether or not to generate indexes per day.

    For example::

        py["compile_day_indexes"] = True


``compile_month_indexes`` (Optional)
    Defaults to ``False``.

    Whether or not to generate indexes per day.

    For example::

        py["compile_month_indexes"] = True



Here's an example of compiling configuration::

   py["compiledir"] = "/home/joe/public_html/compiled_site/"
   py["compile_themes"] = ["html"]
   py["compile_index_themes"] = ["html", "atom"]
   py["compile_day_indexes"] = False
   py["compile_month_indexes"] = True
   py["compile_year_indexes"] = True



Compiling your blog
===================

There are two modes to compile in.


Compile everything
------------------

To compile all pages in your blog, ``cd`` into the directory that
contains your ``config.py`` file and run::

   % douglas-cmd compile

Or from any directory run::

   % douglas-cmd compile --config </path/to/blog_dir>

where ``</path/to/blog_dir>`` is replaced by the path of the directory
that contains your ``config.py`` file.  For example::

   % douglas-cmd compile --config /home/joe/blog/

Or, if the location of your ``config.py`` file is in your
``PYTHONPATH`` (an environment variable) then you can run
``douglas-cmd compile`` from any directory without giving the
``--config`` option.

Lots of output will appear as Douglas figures out all the urls that
need to be rendered and then renders them.


Compiling incrementally
-----------------------

To find all the entries that have changed since you last compiled
and then re-compile just those entries, tack on ``--incremental`` to
the end.

Compiling incrementally works by comparing the mtime of the entry file
with the mtime of the rendered file.


Compiling other URLs
====================

Some plugins provide other URLs that are part of your site, but not
really part of your blog since they're not related to entries.
Examples of this include the plugininfo plugin which provides
information about the plugins that you're running.  You can set the
``compile_urls`` property in ``config.py`` to a list of all the urls
that need to be compiled every time.  This list could include:

* RSS, FOAF, OPML, Atom or any other kind of feeds
* urls for plugins that aren't related to entries (plugininfo,
  pystaticfile, booklist, ...)
* urls for plugins that provide other kinds of indexes (index by tag,
  index by popularity, ...)


``compile_urls`` takes a list of strings where each string is a url
path to be compiled.

For example if I wanted to render the booklist page and the RSS feed
for my main page, I would set it like this::

   py["compile_urls"] = [
       "/index.xml",            # blog feed
       "/pages/about.html",     # about this blog page
       "/booklist/index.html",  # list of books I've read
   ]


Static assets
=============

Douglas can collect all the static assets from the various places they're
located and copy them all over to your ``compiledir``.

Run::

    $ douglas-cmd collectstatic


By default, it looks in the ``static/`` subdirectory of the parent
directory of your datadir as well as the ``static/`` subdirectory of
all your theme directories.

You can tell it to copy over static files from other directories using the
``static_files_dirs`` configuration variable.

For example::

    py['static_files_dirs'] = [
        '/home/joe/blog/staticimages/',
        '/home/joe/blog/blogimages/'
    ]


Things to note
==============

* Both compiling everything and compiling incrementally *won't* remove
  outdated files.

* You probably don't want to compile an RSS or Atom version of every
  blog entry, so don't include those themes in ``compile_themes`` and
  instead specify the urls by hand in ``compile_urls`` or
  ``compile_index_themes``.

* Compiling doesn't copy over static assets---you have to do that separately
  with ``douglas-cmd collectstatic``.


Example setup
=============

I have all my blog files located in ``/home/joe/blog/``.

My blog consists of blog entries and also a CSS file, a JavaScript
file, and a bunch of images.

My directory layout looks like::

   blog/
     |- www/
     |  |- images/
     |  |- css/
     |  \- js/
     |
     |- entries/       # all my blog entries
     |- themedir/      # themes and templates
     |- plugins/       # a couple of plugins I use
     |
     |- config.py      # my config.py file
     \- compile.sh     # shell script below


I render my blog to ``/home/joe/public_html``.

I like having my blog updated nightly---that gives me time to write
entries during the day at my leisure and they all appear the next day.
I do this by having a ``compile.sh`` that gets run by cron every
night.

The script looks like this:

.. code-block:: bash

   #!/bin/bash 

   BLOGDIR=/home/joe/blog
   OUTPUTDIR=/home/joe/public_html
 
   # compile entire blog
   douglas-cmd compile --config ${BLOGDIR} --incremental

   # copy static assets
   douglas-cmd collectstatic --config ${BLOGDIR}

   # copy static files (images, css, ...)
   cp -ar ${BLOGDIR}/compiled_site/* ${OUTPUTDIR}
