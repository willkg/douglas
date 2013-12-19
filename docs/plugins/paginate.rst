
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

===================================================
 paginate - Allows navigation by page for index... 
===================================================

Summary
=======

Plugin for breaking up long index pages with many entries into pages.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.paginate`` to your ``load_plugins`` list
   variable in your ``config.py`` file.

   Make sure it's the first plugin in the ``load_plugins`` list so
   that it has a chance to operate on the entry list before other
   plugins.

2. (optional) Add some configuration to your ``config.py`` file.


Usage
=====

Add the following blurb where you want page navigation to your
``entry_list`` template::

    {{ pager.as_list()|safe }}

which generates HTML like this::

    [1] 2 3 4 5 6 7 8 9 ... >>

Or::

    {{ pager.as_span()|safe }}

which generates HTMl like this::

    Page 1 of 4 >>

You can also do your own pagination. The ``pager`` instance exposes
the following helpful bits:

* ``number`` - the page number being shown
* ``has_next()`` - True if there's a next page
* ``has_previous()`` - True if there's a previous page
* ``link(pageno)`` - Builds the url for the specified page


Configuration variables
=======================

``paginate_previous_text``

   Defaults to "&lt;&lt;".

   This is the text for the "previous page" link.


``paginate_next_text``

   Defaults to "&gt;&gt;".

   This is the text for the "next page" link.


Note about compiling
====================

This plugin works fine with compiling, but the urls look different.
Instead of adding a ``page=4`` kind of thing to the querystring, this
adds it to the url.

For example, say your front page was ``/index.html`` and you had 5
pages of entries. Then the urls would look like this::

    /index.html           first page
    /index_page2.html     second page
    /index_page3.html     third page
    ...


License
=======

Plugin is distributed under license: MIT
