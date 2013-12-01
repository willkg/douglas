
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

===================================================
 paginate - Allows navigation by page for index... 
===================================================

Summary
=======

Plugin for paging long index pages.

douglas uses the ``num_entries`` configuration variable to prevent
more than ``num_entries`` being rendered by cutting the list down to
``num_entries`` entries.  So if your ``num_entries`` is set to 20, you
will only see the first 20 entries rendered.

The paginate plugin overrides this functionality and allows for
paging.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.paginate`` to your ``load_plugins`` list
   variable in your ``config.py`` file.

   Make sure it's the first plugin in the ``load_plugins`` list so
   that it has a chance to operate on the entry list before other
   plugins.

2. (optional) Add some configuration to your ``config.py`` file.

3. Add the following blurb where you want page navigation to your
   entry_list template::

       <p>
         {{ page_navigation|safe }}
       </p>


Configuration variables
=======================

``paginate_previous_text``

   Defaults to "&lt;&lt;".

   This is the text for the "previous page" link.


``paginate_next_text``

   Defaults to "&gt;&gt;".

   This is the text for the "next page" link.


``paginate_linkstyle``

   Defaults to 1.

   This allows you to change the link style of the paging.

   Style 0::

       [1] 2 3 4 5 6 7 8 9 ... >>

   Style 1::

      Page 1 of 4 >>

   If you want a style different than that, you'll have to copy the
   plugin and implement your own style.


Note about static rendering
===========================

This plugin works fine with static rendering, but the urls look
different. Instead of adding a ``page=4`` kind of thing to the
querystring, this adds it to the url.

For example, say your front page was ``/index.html`` and you had 5
pages of entries. Then the urls would look like this::

    /index.html           first page
    /index_page2.html     second page
    /index_page3.html     third page
    ...


License
=======

Plugin is distributed under license: MIT
