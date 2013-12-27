
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

=======================
 tags - Tags plugin... 
=======================

Summary
=======

This plugin allows you to specify the tags your entry has in the
metadata of the entry.  It adds a new command to douglas-cmd to index
all the tags data and store it in a file.

It creates a ``TagManager`` instance in the Jinja2 environment which
you can use to iterate through and display tags data.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.tags`` to the ``load_plugins`` list in your
   ``config.py`` file.

2. Configure as documented below.


Configuration
=============

The following config properties define where the tags file is located,
how tag metadata is formatted, and how tag lists triggered.

``tags_separator``

    This defines the separator between tags in the metadata line.
    Defaults to ",".

    After splitting on the separator, each individual tag is stripped
    of whitespace before and after the text.

    For example::

       Weather in Boston
       #tags weather, boston
       <p>
         The weather in Boston today is pretty nice.
       </p>

    returns tags ``weather`` and ``boston``.

    If the ``tags_separator`` is::

       py["tags_separator"] = "::"

    then tags could be declared in the entries like this::

       Weather in Boston
       #tags weather::boston
       <p>
         The weather in Boston today is pretty nice.
       </p>

``tags_filename``

    This is the file that holds indexed tags data.  Defaults to
    datadir + os.pardir + ``tags.index``.

    This file needs to be readable by the process that runs your blog.
    This file needs to be writable by the process that creates the
    index.

``tags_trigger``

    This is the url trigger to indicate that the tags plugin should
    handle the file list based on the tag.  Defaults to ``tag``.

``truncate_tags``

    If this is True, then tags index listings will get passed through
    the truncate callback.  If this is False, then the tags index
    listing will not be truncated.

    If you're using a paging plugin, then setting this to True will
    allow your tags index to be paged.

    Example::

        py["truncate_tags"] = True

    Defaults to True.


Usage in templates
==================

The ``TagManager`` gets added to the context as ``tags. It has the
following methods:

``all_tags()``
    Returns a list of (tag, tag_url, count) tuples.

    You can iterate over this to render tag data for all the tags
    on your blog.

    ::

        {{ tags.all_tags()|safe }}


``all_tags_div()``
    Generates HTML for a div of class ``allTags`` with ``a`` tags of
    class ``tag`` in it--one for each tag.

    ::

        {{ tags.all_tags_div()|safe }}


``all_tags_cloud()``
    Generates HTML for a div of class ``allTagsCloud`` with ``a`` tags
    of class ``tag`` in it--one for each tag. The ``a`` tags also have
    one of ``biggestTag``, ``bigTag``, ``mediumTag``, ``smallTag``, or
    ``smallestTag`` depending on how "big" the tag should show up in
    the cloud.

    ::

        {{ tags.all_tags_cloud()|safe }}


``entry_tags(entry)``
    Returns a list of (tag, tag_url) tuples for tags for the specified
    entry.

    ::

        {% for tag in tags.entry_tags(entry) %}
          {{ tag }}
        {% endfor %}


``entry_tags_span(entry)``
    Generates HTML for a span of class ``entryTags`` with ``a`` tags
    of class ``tag`` in it--one for each tag.

    ::

        {{ tags.entry_tags_span(entry)|safe }}


.. Note::

   If you use functions that generate HTML in a Jinja2 template, you
   need to run them through the ``|safe`` filter. Otherwise the HTML
   will be escaped.


Creating the tags index file
============================

Run::

    douglas-cmd buildtags

from the directory your ``config.py`` is in or::

    douglas-cmd buildtags --config=/path/to/config/file

from anywhere.

This builds the tags index file that the tags plugin requires to
generate tags-based bits for the request.

Until you rebuild the tags index file, the entry will not have its
tags indexed.  Thus you should either rebuild the tags file after writing
or updating an entry or you should rebuild the tags file as a cron job.

.. Note::

   If you're compiling your blog, you need to build the tags index
   before you compile.


Converting from categories to tags
==================================

This plugin has a command that goes through your entries and adds tag
metadata based on the category.  There are some caveats:

1. it assumes entries are in the blosxom format of title, then
   metadata, then the body.

2. it only operates on entries in the datadir.

It maintains the atime and mtime of the file.  My suggestion is to
back up your files (use tar or something that maintains file stats),
then try it out and see how well it works, and figure out if that
works or not.

To run the command do::

    douglas-cmd categorytotags

from the directory your ``config.py`` is in or::

    douglas-cmd categorytotags --config=/path/to/config/file

from anywhere.


License
=======

Plugin is distributed under license: MIT
