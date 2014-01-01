===================================
Welcome to Douglas's documentation!
===================================

Summary
=======

Douglas is a file-based blog system written in Python with the
following features:

* compiler
* WSGI application
* runs as a CGI script (woo-hoo!)
* plugin system for easy adjustment of transforms
* Jinja renderer
* basic set of built-in plugins

Douglas is a rewrite of `Pyblosxom <http://pyblosxom.github.io>`_.


Quick start
===========

1. Install:

   .. code-block:: bash

      $ pip install https://github.com/willkg/douglas/archive/master.zip#egg=douglas``

2. Create a new blog:

   .. code-block:: bash

      $ douglas-cmd create blog
      $ cd blog

3. Edit the configuration
4. Write a blog entry

   .. code-block:: bash

      $ vi entries/firstpost.txt

5. Compile the blog

   .. code-block:: bash

      $ douglas-cmd compile

6. Copy the static assets (JS, CSS, images, ...)

   .. code-block:: bash

      $ douglas-cmd collectstatic

7. Preview it locally

   .. code-block:: bash

      $ douglas-cmd serve

8. Copy it to your server


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
   config_variables
   writing_entries
   themes_and_templates
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
   dev_release


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
