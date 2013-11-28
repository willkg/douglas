
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

================================
 draft_folder - Draft folder... 
================================

Summary
=======

Enables drafts for your blog.


Install and Configure
=====================

1. Add ``douglas.plugins.draft_folder`` to the ``load_plugins`` list
   in your ``config.py`` file.

2. Set ``py["draftdir"]`` to the directory where your draft entries
   will be.

   This can't be a subdirectory of your datadir.

   Make sure to create this directory, too.

3. (optional) Set ``py["draft_trigger"]`` in your ``config.py`` file
   to the url path you want to show drafts in. This defaults to
   ``draft``.

That's it!


License
=======

Plugin is distributed under license: MIT
