.. Douglas documentation master file, created by sphinx-quickstart on
   Mon Feb 16 00:26:34 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======================================
 Welcome to Douglas's documentation!
=======================================

.. _part-one:

Part 1: Douglas user manual
=============================

Documentation for installing, configuring and tweaking Douglas for your
purposes.

.. toctree::
   :maxdepth: 2

   about_douglas
   license
   whatsnew
   douglas_cmd
   deploy_compiled
   deploy_cgi
   deploy_paste
   deploy_apache_mod_wsgi
   deploy_lighttpd_fastcgi
   config_variables
   writing_entries
   themes_and_templates
   renderers
   plugins
   authors


.. _part-two:

Part 2: Core plugin documentation
=================================

Documentation for plugins that come with Douglas.

.. toctree::
   :titlesonly:
   :glob:

   plugins/*


Part 3: Developer documentation
===============================

Documentation anyone interested in hacking on Douglas, writing
plugins, or things of that ilk.

.. toctree::
   :maxdepth: 2

   dev_contributing
   dev_architecture
   dev_writing_plugins
   dev_codedocs
   dev_testing
   dev_release


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
