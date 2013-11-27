.. _deploy-paste-chapter:

================================
 Deploying Douglas with Paste
================================

Summary
=======

Douglas 1.4 and later support Paste.  This document covers
installing and using Douglas with Paste.

This installation assumes you have some understanding of Python Paste.
If this doesn't sound like you, then you can read up on Paste on the
`Paste website`_ or the `Wikipedia page`_.


.. _Paste website: http://pythonpaste.org/
.. _Wikipedia page: http://en.wikipedia.org/wiki/Python_Paste

Dependencies
============

You'll need:

* Python Paste which can be found at http://pythonpaste.org/

Install::

    pip install pastescript


Deployment for testing
======================

Create a new blog by doing::

    douglas-cmd create <BLOG-DIR>

Then do::

    cd <BLOG-DIR>
    paster serve blog.ini

The ``paster`` script will print the URL for your blog on the command
line and your blog is now available on your local machine to a browser
on your local machine.

This allows you to test your blog and make sure it works.


Paste .ini file configuration
=============================

Paste configuration is done in an ``.ini`` file.

Edit the ``blog.ini`` file that ``douglas-cmd`` created for you.

The ``[server:main]`` section dictates how Paste is serving your
blog.  See the `Paste documentation`_ for more details on this
section.

.. _Paste documentation: http://pythonpaste.org/


The ``[app:main]`` section specifies the Douglas WSGI application
function and the directory your ``config.py`` file is in.  A
sample is here::

    [app:main]
    paste.app_factory = Douglas.douglas:douglas_app_factory
    configpydir = /home/joe/blog/

Additionally, you can override ``config.py`` values in your
``blog.ini``.  For example, this overrides the ``blog_title``
value::

    [app:main]
    paste.app_factory = Douglas.douglas:douglas_app_factory
    configpydir = /home/joe/blog/

    # Douglas config here
    blog_title = Joe's Blog

This is really handy for testing changes to your blog infrastructure.
