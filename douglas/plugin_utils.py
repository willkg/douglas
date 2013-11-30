"""
Holds a series of utility functions for cataloguing, retrieving, and
manipulating callback functions and chains.  Refer to the documentation
for which callbacks are available and their behavior.
"""

import os
import glob
import sys
import os.path
import traceback


# This holds the list of plugins that have been loaded.  If you're running
# Douglas as a long-running process, this only gets cleared when the
# process is restarted.
plugins = []


# This holds a list of callbacks (any function that begins with cp_)
# and the list of function instances that support that callback.  If
# you're running Douglas as a long-running process, this only gets
# cleared when the process is restarted.
callbacks = {}


# This holds a list of (plugin name, exception) tuples for plugins that
# didn't import.
bad_plugins = []


class PluginDirDoesntExist(Exception):
    pass


def catalogue_plugin(plugin_module):
    """
    Goes through the plugin's contents and catalogues all the functions
    that start with cb_.  Functions that start with cb_ are callbacks.

    :arg plugin_module: the module to catalogue
    """
    listing = [item for item in dir(plugin_module) if item.startswith("cb_")]

    for mem in listing:
        func = getattr(plugin_module, mem)
        if callable(func):
            callback_name = mem[3:]
            callbacks.setdefault(callback_name, []).append(func)


def get_callback_chain(chain):
    """
    Returns a list of functions registered with the callback.

    :returns: list of functions registered with the callback (or an
        empty list)
    """
    return callbacks.get(chain, [])


def initialize_plugins(plugin_dirs, plugin_list, raiseerrors=True):
    """Imports and initializes plugins

    Adds paths specified by "plugins_dirs" to the sys.path and then
    imports and initializes all plugins listed in "plugin_list" in
    the order specified.

    .. Note::

       If Douglas is part of a long-running process, you must
       restart Douglas in order to pick up any changes to your plugins.

    :arg plugin_dirs: the list of directories to add to the sys.path
        because that's where our plugins are located.

    :arg plugin_list: the list of plugins to load.

    :arg raiseerrors: whether or not to throw an exception if
        a plugin throws an exception when loading

    """
    # This makes sure we only import and initialize once.
    if plugins or bad_plugins:
        return

    # Clear out callbacks list.
    callbacks.clear()

    # Add directories to sys.path
    for mem in plugin_dirs:
        if os.path.isdir(mem):
            sys.path.append(mem)
        else:
            raise PluginDirDoesntExist(
                'Plugin directory "{0}" does not exist.  '
                'Please check your config file.'.format(mem))

    for mem in plugin_list:
        try:
            _module = __import__(mem)

        except (SystemExit, KeyboardInterrupt):
            raise

        except:
            # This needs to be a catch-all.
            if raiseerrors:
                raise

            bad_plugins.append((mem, "".join(traceback.format_exc())))
            continue

        for comp in mem.split(".")[1:]:
            _module = getattr(_module, comp)

        catalogue_plugin(_module)
        plugins.append(_module)
