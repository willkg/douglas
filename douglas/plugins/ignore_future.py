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
    # FIXME - This can be expensive depending on how filestat is
    # implemented and should cache the data in a file like the tags
    # plugin does.
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
