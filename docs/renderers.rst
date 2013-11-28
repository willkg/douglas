.. _renderers:

=========
Renderers
=========

Douglas supports multiple renderers and comes with two by default:
debug and Jinja2.


blosxom renderer
================

You can set which renderer to use in your ``config.py`` file like
this::

    py["renderer"] = "debug"


.. Note::

    If you don't specify the ``renderer`` configuration variable, 
    Douglas uses the Jinja2 renderer.


debug renderer
==============

The debug renderer outputs your blog in a form that makes it easy to 
see the data generated when handling a Douglas request.  This is 
useful for debugging plugins, working on Jinja2 themes and
templates, and probably other things as well.

To set Douglas to use the debug renderer, do this in your
``config.py`` file::

    py["renderer"] = "debug"


Other renderers
===============

If you want your blog rendered by a different renderer, say one that
uses a different template system like Cheetah, then you will
need to install a plugin that implements the ``renderer`` callback.
