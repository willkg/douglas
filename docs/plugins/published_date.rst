
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

=========================================================
 published_date - Maintain published date in file met... 
=========================================================

Summary
=======

This takes a #published date/time stamp in the entry and returns
that as the mtime.

Example entry::

   My first post!
   #published 2008-01-01 12:20:22
   <p>
     This is my first post!
   </p>


returns an mtime of 01-01-2008 at 12:20:22.


Install
=======

Add ``douglas.plugins.published_date`` to the ``load_plugins`` list of
your ``config.py`` file.


License
=======

Plugin is distributed under license: MIT
