
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

=====================================================
 rst_parser - restructured text support for blog ... 
=====================================================

Summary
=======

A reStructuredText entry formatter for douglas.  reStructuredText is
part of the docutils project (http://docutils.sourceforge.net/).  To
use, you need a *recent* version of docutils.  A development snapshot
(http://docutils.sourceforge.net/#development-snapshots) will work
fine.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.rst_parser`` to the ``load_plugins`` list
   in your ``config.py`` file.

2. Install docutils.  Instructions are at
   http://docutils.sourceforge.net/


Configuration
=============

There's two optional configuration parameter you can for additional
control over the rendered HTML::

   # To set the starting level for the rendered heading elements.
   # 1 is the default.
   py['reST_initial_header_level'] = 1

   # Enable or disable the promotion of a lone top-level section title to
   # document title (and subsequent section title to document subtitle
   # promotion); disabled by default.
   py['reST_transform_doctitle'] = 0


.. Note::

   If you're not seeing headings that you think should be there, try
   changing the ``reST_initial_header_level`` property to 0.


Usage
=====

Blog entries with a ``.rst`` extension will be parsed as
reStructuredText.

Blog entries can have a summary. Insert a break directive at the point
where the summary should end. For example::

    First part of my blog entry....

    .. break::

    Second part of my blog entry after the fold.

Some entries don't have a summary attribute, so if you're going to
show the summary, you need to make sure it's defined first.

For example, in your entry_list template, you could show the summary
like this::

    {% if entry.summary is defined %}
      {{ entry.summary|safe }}
      <p><a href="{{ entry.url }}">Read more...</a></p>
    {% else %}
      {{ entry.body|safe }}
    {% endif %}


License
=======

Plugin is distributed under license: MIT
