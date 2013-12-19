
.. only:: text

   This document file was automatically generated.  If you want to edit
   the documentation, DON'T do it here--do it in the docstring of the
   appropriate plugin.  Plugins are located in ``douglas/plugins/``.

==============================================
 categories - Builds a list of categories.... 
==============================================

Summary
=======

Walks through your blog root figuring out all the categories you have
and how many entries are in each category.  It generates html with
this information and stores it in the ``$(categorylinks)`` variable
which you can use in your head or foot templates.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.pycategories`` to the ``load_plugins`` list
   in your ``config.py`` file.


Configuration
=============

There is no configuration.


Usage
=====

Categories plugin provides an HTML version of the categories in a list
form. You can use it in your template like this::

    {{ categories.as_list()|safe }}


Alternatively, you can build the categories HTML yourself::

    {% for cat, count in categories.categorydata %}
        ....
    {% endfor %}


License
=======

Plugin is distributed under license: MIT
