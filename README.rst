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


Quickstart for compiling a new blog
===================================

1. Create a virtual environment
2. Activate the virtual environment
3. Install Douglas into your virtual environment::

       pip install https://github.com/willkg/douglas/archive/master.zip#egg=douglas

4. Create a new blog structure::

       douglas-cmd create <blog-dir>

   For example: ``douglas-cmd create blog``

5. Edit the ``blog/config.py`` file. There should be instructions
   on what should get changed and how to change it.

6. Change directories to ``blog`` and then render the site::

       douglas-cmd compile

7. Collect the static assets::

       douglas-cmd collectstatic

8. Copy the ``compiled_site/`` directory tree to where they're
   available for serving by your web server.


Where to go from here
=====================

Each file in ``blog/entries/`` is a blog entry. They are text files.
You can edit them with any text editor.

The blog is rendered using Jinja2.  The templates are in the
``blog/themes/`` directory.  A theme consists of:

* a ``content_type`` file which has the mimetype of the output being rendered
  (e.g. ``text/html``)
* an ``entry.<themename>`` file which is used when rendering a page
  with a single entry
* an ``entry_list.<themename>`` file which is used when rendering a
  page with a bunch of entries (e.g. category list, date archive list,
  front page, ...)
* additional template files required by plugins as specified by those plugins
* static assets like CSS files, JS files and images in the
  ``static/<themename>/`` subdirectory

The following plugins which come with Douglas are enabled by default
in your ``load_plugins`` config property:

``douglas.plugins.draft_folder``

    Creates a draft folder that you can view on the web-site, but
    doesn't show up in the archive links.  This makes it easier for
    other people to review entries before they're live.

    The draft dir is ``blog/drafts/``.

    When you want to make an entry live, you move it from
    ``blog/drafts/`` to ``blog/entries/``.

``douglas.plugins.published_date``

    Add ``#published YYYY-MM-DD HH:MM`` to the metadata in your blog
    entries. That's the published date for the blog entry rather than
    the mtime of the file.

Douglas comes with other useful plugins. Refer to the documentation for a list.

You can write your own plugins and put the plugin files in
``blog/plugins/`` and add the plugin Python module to the
``load_plugins`` list in your ``config.py`` file.
