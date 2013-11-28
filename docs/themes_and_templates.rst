.. _themes-and-templates:

====================
Themes and Templates
====================

Summary
=======

This chapter covers writing a theme for Douglas.  The default renderer
is `Jinja2 <http://jinja.pocoo.org/docs/>`_. You can set up other
renderers using plugins.  See the chapter on:ref:`renderers <renderers>`
for more details.


Themes and templates
====================

A theme consists of at least:

* a ``content_type`` file which has the mimetype of the output being rendered
  (e.g. ``text/html``)
* an ``entry.<themename>`` file which is used when rendering a page
  with a single entry
* an ``entry_list.<themename>`` file which is used when rendering a
  page with a bunch of entries (e.g. category list, date archive list,
  front page, ...)

Plugins may require additional templates. See the plugin's documentation
for details.


Example blog
------------

Joe has this set in his ``config.py`` file::

    py["themedir"] = "/home/joe/blog/themes/"


Joe's blog directory structure looks like this::

   /home/joe/blog/
             |- entries/             <-- datadir
             |  |- work/             <-- work category of entries
             |  |- home/             <-- home category of entries
             |
             |- themes/
                |- html/             <-- html theme
                |  |- content_type
                |  |- entry.html
                |  |- entry_list.html
                |
                |- rss/              <-- rss theme
                   |- content_type
                   |- entry.rss
                   |- entry_list.rss


.. Note::

   There's some redundancy between the theme named directory and
   the theme in the extension. Having the theme in the extension
   makes it more likely your editor will use the right syntax
   highlighting. So that's helpful. Having themes in separate
   directories means that if you have a bunch of files, they don't
   overlap and get all confuzzled. That's helpful, too.


Template writing tips
=====================

We're using Jinja2, so we reference variables using Jinja2 syntax and we can
use Jinja2 blocks, built-in functions and built-in filters.

This prints a variable::

    {{ foo }}

You can iterate through a list::

    {% for entry in content %}
        {{ entry.title }}
        ...
    {% endfor %}

Douglas has autoescaping set, so if the variable you're printing
is HTML and you know that it's safe, you can use the ``safe`` filter::

    {{ entry.body|safe }}

Templates can inherit from other templates. It's probably the case
you want to have a base layout template that defines the common
parts of your site, then have the entry or entry-list specific
stuff in those templates.

To inherit from another template, use the ``extends`` tag::

    {% extends "filename.ext" %}

In the "super template" you can define blocks and override those
blocks in the "sub templates".

See the included html theme for an example.

.. seealso::

   http://jinja.pocoo.org/

   http://jinja.pocoo.org/docs/templates/

   http://jinja.pocoo.org/docs/templates/#template-inheritance


Template variables
==================

This is the list of variables that are available to your templates.
Templates contain variables that are expanded when the template is
rendered.  Plugins may add additional variables---refer to plugin
documentation for a list of which variables they add and in which
templates they're available.


Getting a complete list of variables
------------------------------------

To get a complete list of what variables are available in your blog,
use the debug renderer by changing the value of the ``renderer``
property in your ``config.py`` file to ``debug`` like this::

   py["renderer"] = "debug"


That will tell you all kinds of stuff about the data structures
involved in the request.  Don't forget to change it back when you're
done!


Variables from config.py
------------------------

Anything in your ``config.py`` file is a variable available to all of
your templates.  For example, these standard properties in your
``config.py`` file are available:

* ``blog_description``
* ``blog_title``
* ``blog_language``
* ``blog_encoding``
* ``blog_author``
* ``blog_email``
* ``base_url`` (if you provided it)
* ...


Additionally, any other properties you set in ``config.py`` are
available in your templates.  If you wanted to create a
``blog_images`` variable holding the base url of the directory with
all your images in it::

   py["blog_images"] = "http://example.com/~joe/images/"


to your ``config.py`` file and it would be available in all your
templates.


Calculated template variables
-----------------------------

These template variables are available to all templates as well.  They
are calculated based on the request.

``root_datadir``
   The root datadir of this page?

   Example: ``/home/subtle/blosxom/weblogs/tools/douglas``

``url``
   The PATH_INFO to this page.

   Example: ``douglas/weblogs/tools/douglas``

``theme``
   The theme that's being used to render this page.

   Example: ``html``

``latest_date``
   The date of the most recent entry that is going to be rendered.

   Example: ``Tue, 15 Nov 2005``

``latest_w3cdate``
   The date of the most recent entry that is going to be rendered in 
   w3cdate format.

   Example: ``2005-11-13T17:50:02Z``

``latest_rfc822date``
   The date of the most recent entry that is going to show in RFC 822 
   format.

   Example: ``Sun, 13 Nov 2005 17:50 GMT``

``pi_yr``
   The four-digit year if the request indicated a year.

   Example: ``2002``

``pi_mo``
   The month name if the request indicated a month.

   Example: ``Sep``

``pi_da``
   The day of the month if the request indicated a day of the month.

   Example: ``15``

``pi_bl``
   The entry the user requested to see if the request indicated a
   specific entry.

   Example: ``weblogs/tools/douglas``

``douglas_version``
   The version number and release date of the douglas version you're
   using.

   Example: ``1.2 3/25/2005``


Variables available in the content entries
------------------------------------------

These template variables are available in the entries.

``title``
   The title of the entry.

   Example: ``First Post!``

``body``
   The text of the entry in HTML.

   Example: ``<p>This is my first post!</p>``

``filename``
   The absolute path of the blog entry file on the file system.

   Example: ``/home/subtle/blosxom/weblogs/tools/douglas/firstpost.txt``

``file_path``
   The filename and extension of the file that the entry is stored in.

   Example: ``firstpost.txt``

``basename``
   The filename without directory or file extension.

   Example: ``firstpost``

``absolute_path``
   The category/path of the entry (from the perspective of the url).

   Example: ``weblogs/tools/douglas``

``path``
   The category/path of the entry.

   Example: ``weblogs/tools/douglas``

``tb_id``
   The trackback id of the entry.

   Example: ``_firstpost``

``yr``
   The four-digit year of the mtime of this entry.

   Example: ``2004``

``mo``
   The month abbreviation of the mtime of this entry.

   Example: ``Jan``

``mo_num``
   The zero-padded month number of the mtime of this entry.

   Example: ``01``

``ti``
   The 24-hour hour and minute of the mtime of this entry.

   Example: ``16:40``

``date``
   The date string of the mtime of this entry.

   Example: ``Sun, 23 May 2004``

``w3cdate``
   The date in w3cdate format of the mtime of this entry.

   Example: ``2005-11-13T17:50:02Z``

``rfc822date``
   The date in RFC 822 format of the mtime of this entry.

   Example: ``Sun, 13 Nov 2005 17:50 GMT``

``fulltime``
   The date in YYYYMMDDHHMMSS format of the mtime of this entry.

   Example: ``20040523164000``

``timetuple``
   The time tuple (year, month, month-day, hour, minute, second,
   week-day, year-day, isdst) of the mtime of this entry.

   Example: ``(2004, 5, 23, 16, 40, 0, 6, 144, 1)``

``mtime``
   The mtime of this entry measured in seconds since the epoch.

   Example: ``1085348400.0``

``dw``
   The day of the week of the mtime of this entry.

   Example: ``Sunday``

``da``
   The day of the month of the mtime of this entry.

   Example: ``23``


Also, any variables created by plugins that are entry-centric and any
variables that come from metadata in the entry are available.  See
those sections in this document for more details.


Template variables from plugins
-------------------------------

Many plugins will create additional variables that are available in
templates.  Refer to the documentation of the plugins that you have
installed to see what variables are available and what they do.


Template variables from entry metadata
--------------------------------------

You can add metadata to your entries on an individual basis and this
metadata is available to your story templates.

For example, if I had a blog entry like this::

   First Post!
   #mood happy
   #music The Doors - Break on Through to the Other Side
   <p>
     This is the first post to my new Douglas blog.  I've
     also got two metadata items in it which will be available
     as variables!
   </p>


You'll have two variables ``$mood`` and ``$music`` that will also be
available in your story templates.


Invoking a theme
================

The theme for a given page is specified in the extension of the file
being requested.  For example:

* ``http://example.com/`` - 
  brings up the index in the default theme which is "html"

* ``http://example.com/index.html`` - 
  brings up the index in the "html" theme

* ``http://example.com/index.rss`` -
  brings up the index in the "rss" theme (which by default is RSS 0.9.1)

* ``http://example.com/2004/05/index.joy`` -
  brings up the index for May of 2004 in the "joy" theme


Additionally, you can specify the theme by adding a ``theme``
variable in the query-string.  Examples:

* ``http://example.com/`` -
  brings up the index in the default theme which is "html"

* ``http://example.com/?theme=rss`` -
  brings up the index in the "rss" theme

* ``http://example.com/2004/05/index?theme=joy`` -
  brings up the index for May of 2004 in the "joy" theme


Setting default theme
=====================

You can change the default theme from ``html`` to some other theme
in your ``config.py`` file with the ``default_theme`` property::

   py["default_theme"] = "joy"


Doing this will set the default theme to use when the URI the user
has used doesn't specify which theme to use.

This url doesn't specify the theme to use, so it will be rendered
with the default theme::

   http://example.com/cgi-bin/douglas.cgi/2005/03

This url specifies the theme, so it will be rendered with that
theme::

   http://example.com/cgi-bin/douglas.cgi/2005/03/?theme=html


Order of operations to figure out which theme to use
====================================================

We know that you can specify the default theme to use in the
``config.py`` file with the ``default_theme`` property.  We know
that the user can specify which theme to use by the file extension
of the URI.  We also know that the user can specify which theme to
use by using the ``flav`` variable in the query string.

The order in which we figure out which theme to use is this:

1. look at the URI extension: if the URI has one, then we use that.
2. look at the ``theme`` querystring variable: if there is one, 
   then we use that.
3. look at the ``default_theme`` property in the ``config.py`` 
   file: if there is one, then we use that.
4. use the ``html`` theme.
