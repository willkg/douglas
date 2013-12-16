=============
About Douglas
=============

What is this?
=============

Douglas is a file-based blog system written in Python with the following features:

* compiler
* WSGI application
* runs as a CGI script (woo-hoo!)
* plugin system for easy adjustment of transforms
* Jinja renderer
* basic set of built-in plugins

Douglas is a rewrite of `Pyblosxom <http://pyblosxom.github.io>`_.


Project
=======

:Code:    https://github.com/willkg/douglas
:License: MIT
:Issues:  https://github.com/willkg/douglas/issues
:Docs:    https://douglas.readthedocs.org/
:Status:  **Extreme Alpha**


Requirements
============

* Python 2.7
* possibly other requirements depending on what plugins you install


Quickstart for compiling
========================

1. Create a virtual environment
2. Activate the virtual environment
3. Install Douglas into your virtual environment::

       pip install https://github.com/willkg/douglas/archive/master.zip#egg=douglas

4. Create a new blog structure::

       douglas-cmd create <blog-dir>

   For example: ``douglas-cmd create mynewblog``

5. Edit the ``mynewblog/config.py`` file. There should be instructions
   on what should get changed and how to change it.

6. Change directories to ``mynewblog`` and then render the site::

       douglas-cmd compile

7. Copy the files from the ``compiled_site/`` dir to where they're
   available for serving by your web server.


Where to go from here
=====================

Each file in ``mynewblog/entries/`` is a blog entry. They are text
files.  You can edit them with your favorite text editor.

The blog is rendered using Jinja2 templates in the
``mynewblog/themes/`` directory.  A theme consists of at least:

* a ``content_type`` file which has the mimetype of the output being rendered
  (e.g. ``text/html``)
* an ``entry.<themename>`` file which is used when rendering a page
  with a single entry
* an ``entry_list.<themename>`` file which is used when rendering a
  page with a bunch of entries (e.g. category list, date archive list,
  front page, ...)

The following plugins which come with Douglas are enabled by default in
your ``load_plugins`` config property:

``douglas.plugins.draft_folder``

    Creates a draft folder that you can view on the web-site, but doesn't
    show up in the archive links.  This makes it easier for other people
    to review entries before they're live.

    The draft dir is ``mynewblog/drafts/``.

    When you want to make an entry live, you move it from
    ``mynewblog/drafts/`` to ``mynewblog/entries/``.

``douglas.plugins.published_date``

    Add ``#published YYYY-MM-DD HH:MM`` to the metadata in your blog
    entries. That's the published date for the blog entry rather
    than the mtime of the file.

Douglas comes with other useful plugins. Refer to the documentation for a list.

You can write your own plugins and put them in ``mynewblog/plugins/``. When
you do this, make sure to add the plugin Python module to the ``load_plugins``
list in your ``config.py`` file.


Overview of Douglas
===================

Entries, categories, storage:

* Douglas stores everything as files on the file system---there is
  no database.
* Each blog entry is a file.
* Blog entry files are stored in a directory hierarchy in your *datadir*.
* Each subdirectory in your *datadir* corresponds to a category of
  your blog.

Themes:

* A theme consists of a set of Jinja *templates*. A theme is an output
  format.
* Themes are stored in a directory called the *themedir*.
* Douglas comes with two themes: html, rss.
* A theme is stored in the *themedir* by name and consists of at least an
  ``index.<name>`` file and a ``content_type`` file.
* There's more information on themes and templates in
  the Themes and Templates chapter of the manual
  (``docs/themes_and_templates.rst`` if you're looking at the source).

Plugins:

* Douglas has a plugin system.
* Plugins are written in Python.
* Plugins are loaded using the ``plugin_dirs`` and ``load_plugins``
  configuration variables.
* Douglas comes with a handful of plugins.
* For more information on using plugins, see Plugins in the manual
  (``docs/plugins.rst`` if you're looking at the source).
* For more information on writing plugins see Writing Plugins
  (``docs/dev_writing_plugins.rst`` if you're looking at the source).
