
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

=======================================================
 yeararchives - Builds year-based archives listing.... 
=======================================================

Summary
=======

Walks through your blog root figuring out all the available years for
the archives list.  Handles year-based indexes.  Builds a list of years
your blog has entries for which you can use in your template.


Install
=======

This plugin comes with Douglas.  To install, do the following:

1. Add ``douglas.plugins.yeararchives`` to the ``load_plugins`` list
   in your ``config.py`` file.


Usage
=====

Add::

    {{ yeararchives.as_list()|safe }}

to the appropriate place in your template.

When the user clicks on one of the year links (e.g.
``http://example.com/2004/``), then yeararchives will display a
summary page for that year.


License
=======

Plugin is distributed under license: MIT
