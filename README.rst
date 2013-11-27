=================
 About Pyblosxom
=================

What is this?
=============

This is the WILLCAGE EXTREME FURY version of Pyblosxom. This is
tweaked for my blog.

See `pyblosxom official site <http://pyblosxom.github.io>`_ for
the official pyblosxom.


Requirements
============

* Python 2.7
* possibly other requirements depending on what plugins you install


Pyblosxom quickstart for static rendering
=========================================

1. Create a virtual environment
2. Activate the virtual environment
3. Install Pyblosxom into your virtual environment::

       pip install https://github.com/willkg/pyblosxom/archive/master.zip#egg=pyblosxom

4. Create a new blog structure::

       pyblosxom-cmd create <blog-dir>

   For example: ``pyblosxom-cmd create mynewblog``

5. Edit the ``mynewblog/config.py`` file. There should be instructions
   on what should get changed and how to change it.

6. From ``mynewblog``, render the site::

       pyblosxom-cmd staticrender

7. Copy the files from the compiled/ dir to where they're available for
   serving by your web server.


Where to go from here
=====================

Each file in ``mynewblog/entries/`` is a blog entry. They are text files.
You can edit them with your favorite text editor.

The blog is rendered using templates in the ``mynewblog/flavours/``
directory. A flavour consists of at least content_type, head, story and
foot templates. You can have date_head and date_foot as well.

The following plugins are used by default:

**draft_folder**

    Creates a draft folder that you can view on the web-site, but doesn't
    show up in the archive links. This makes it easier for other people
    to review entries before they're live.

    The draft dir is ``mynewblog/drafts/``.

    When you want to make an entry live, you move it from
    ``mynewblog/drafts/`` to ``mynewblog/entries/``.

**published_date**

    Add ``#pyblished YYYY-MM-DD HH:MM`` to your file metadata and that's
    the published date for the blog entry rather than the mtime of the
    file.


Overview of Pyblosxom
=====================

Entries, categories, storage:

* Pyblosxom stores everything as files on the file system---there is
  no database.
* Each blog entry is a file.
* Blog entry files are stored in a directory hierarchy in your *datadir*.
* Each subdirectory in your *datadir* corresponds to a category of
  your blog.

Themes:

* Themes in Pyblosxom are called *flavours*.
* A flavour consists of a set of *templates*.
* Flavours are stored in a directory called the *flavourdir*.
* Pyblosxom comes with several flavours: html, rss20, and atom.
* The `website <http://pyblosxom.github.com/>`_ maintains a flavour
  registry for flavours contributed by people like you.
* There's more information on flavours and templates in
  the Flavours and Templates chapter of the manual
  (``docs/flavours_and_templates.rst`` if you're looking at the source).

Plugins:

* Pyblosxom has a plugin system.
* Plugins are written in Python.
* Plugins are loaded using the ``plugin_dirs`` and ``load_plugins``
  configuration variables.
* The `website <http://pyblosxom.github.com/>`_ maintains a plugin
  registry for plugins submitted by people like you.
* For more information on using plugins, see Plugins in the manual
  (``docs/plugins.rst`` if you're looking at the source).
* For more information on writing plugins see Writing Plugins
  (``docs/dev_writing_plugins.rst`` if you're looking at the source).
