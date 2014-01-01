.. highlight:: python
   :linenothreshold: 5

.. _writing-plugins:

===============
Writing Plugins
===============

Summary
=======

This chapter covers a bunch of useful things to know when writing
Douglas plugins.  This chapter, moreso than the rest of this manual,
is very much a work in progress.

If you need help with plugin development, write up an issue in the
issue tracker.

FIXME - this needs more work


Things that all plugins should have
===================================

This section covers things that all plugins should have.  This makes
plugins easier to distribute, maintain, update, and easier for users
to use them.


Example
-------

Here's a really short example plugin named ``ignore_future.py``:

.. code-block:: python
   
   """
   Summary
   =======
    
   Prevents blog entries published in the future from showing up on
   the blog.
    
    
   Install
   =======
    
   Add ``douglas.plugins.ignore_future`` to the ``load_plugins`` list in
   your ``config.py`` file.
    
   """
    
   __description__ = "Ignores entries in the future."
   __category__ = "content"
   __license__ = "MIT"
    
   import time
    
   from douglas.tools import filestat
    
    
   def cb_entries(args):
       cfg = args['config']
       entry_files = args['entry_files']
    
       now = time.time()
    
       def check_mtime(cfg, now, path):
           mtime = time.mktime(filestat(cfg, path))
           return mtime < now
    
       entry_files = [path for path in entry_files
                      if check_mtime(cfg, now, path)]
       args['entry_files'] = entry_files
    
       return args
    

Name
----

All plugins need a good name that's unique so that your plugin doesn't
get confused with other plugins.  Additionally, the filename for your
plugin needs to be unique.

.. Warning::

   Make sure the filename for your plugin is unique!  Douglas imports
   your plugin using Python import machinery which means that if your
   plugin has the same name as a package on your system, then
   depending on how ``sys.path`` is set up, Douglas may load the
   package on your system and NOT your plugin.

   If you think this might be happening to you, do ``douglas-cmd
   test`` and it'll tell you the paths of what it's loading.


Documentation
-------------

All plugins should have a docstring at the top of the file that
explains what the plugin does, how to install it, how to configure it
and how to use it.


Metadata
--------

All plugins should have the following module-level variables 
defined in them just after the docstring:

* ``__description__`` - This is a one-sentence description of what your 
  plugin does.

* ``__license__`` - The license this plugin is distributed under.

* ``__category__`` - (Optional) A one-word category for the plugin. You
  only need to include this if you're planning to create a pull request
  to add this plugin to Douglas core plugins.

* ``__url__`` (Optional) The canonical url where information about
  this plugin is. GitHub repository, web-site, author's blog
  entry---whatever. Users will use this url to figure out whether
  their copy of the plugin is up-to-date, contact the author with
  issues, etc.


Configuration, installation and verification
--------------------------------------------

After that, you could have a ``verify_installation`` function that
verifies that the plugin is configured correctly. This helps when your
plugin has complex configuration since you can walk the user through
misconfiguration issues rather than the user see your plugin fail
inexplicably.

If your plugin doesn't require much configuration or the configuration
is trivial, feel free to skip this.

Here's an example:

.. code-block:: python

   def verify_installation(request):
       cfg = request.get_configuration()

       if 'important_key' not in cfg:
           print 'You are missing important_key in your configuration!'
	   return False
       return True


Return ``False`` if it fails verification.

Return ``True`` if it passes verification.


How to log to the log file
==========================

The user can configure logging in their ``config.py`` file. If it's
not configured, then logging is at the ``error`` level and is piped to
stdout.

Douglas uses the `Python logging module
<http://docs.python.org/2/library/logging.html>`_.


How to implement a callback
===========================

If you want to implement a callback, you add a function corresponding
to the callback name to your plugin module.  For example, if you
wanted to modify the Request object just before rendering, you'd
implement ``cb_prepare`` like this::

    def cb_prepare(args):
        pass


Obviously, since we have ``pass`` we're not actually doing anything
here, but when the user sends a request and Douglas handles it, this
function in your plugin will get called when Douglas runs the
prepare callback.

Each callback passes in arguments through a single dictionary.  Each
callback passes in different arguments and expects different return
values.  Check the doc:`dev_architecture <architecture>` chapter
for a list of all the callbacks that are available, their arguments,
and how they work.


.. _writing-an-entryparser:

Writing an entryparser
======================

FIXME - write this


Writing a renderer
==================

FIXME - write this


.. _writing-a-command:

Writing a plugin that adds a commandline command
================================================

The ``douglas-cmd`` command allows for plugin-defined commands.
This allows your plugin to do maintenance tasks (updating an index,
statistics, generating content, ...) and allows the user to schedule
command execution through cron or some similar system.

To write a new command, you must:

1. implement the ``commandline`` callback which adds the command,
   handler, and command summary

2. implement the command function

For example, this adds a command to print command line arguments:

.. code-block:: python

   def printargs(command, argv):
       print argv
       return 0

   def cb_commandline(args):
       args["printargs"] = (printargs, "prints arguments")
       return args


Executing the command looks like this::

    % douglas-cmd printargs a b c
    douglas-cmd version 0.1
    a b c


For examples, see ``douglas/cmdline.py`` and
``douglas/plugins/tags.py``.
