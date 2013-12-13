=============================
Douglas on the command line
=============================

Douglas comes with a command line tool called ``douglas-cmd``.  It allows
you to create new blogs, verify your configuration, run compiling,
render single urls, and run command line functions implemented in plugins.

For help, do::

    douglas-cmd --help

It'll list the commands and options available.

If you tell it where your config file is, then it'll list commands and
options available as well as those implemented in plugins you have installed.

For example::

    douglas-cmd --config=/path/to/config.py --help

For more information on compiling, see :ref:`compiling`.
