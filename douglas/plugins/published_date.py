"""
Summary
=======

This takes a #published date/time stamp in the entry and returns
that as the mtime.

Example entry::

   My first post!
   #published 2008-01-01 12:20:22
   <p>
     This is my first post!
   </p>


returns an mtime of 01-01-2008 at 12:20:22.


Install
=======

Add ``douglas.plugins.published_date`` to the ``load_plugins`` list of
your ``config.py`` file.

"""

__description__ = "Maintain published date in file metadata."
__category__ = "metadata"
__license__ = 'MIT'

import stat
import time

from douglas.memcache import memcache_decorator


def parse_date(d):
    for fmt in ('%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d'):
        try:
            return time.strptime(d, fmt)
        except ValueError:
            pass

    raise ValueError('time data {0} format is not recognized'.format(d))


@memcache_decorator('published_date')
def get_date(fn):
    """Returns time tuple or None for published time of file."""
    try:
        with open(fn, 'r') as fp:
            lines = fp.readlines()
    except IOError:
        return None

    for line in lines:
        if line.startswith('#published'):
            try:
                d = line.split(' ', 1)[1].strip()
                d = parse_date(d)
                return tuple(d)
            except IndexError:
                # An IndexError indicates that there is no actual date
                # after the #published keyword.
                return None

    return None


def cb_filestat(args):
    filename = args['filename']
    mtime = args['mtime']

    d = get_date(filename)
    if d:
        if len(d) == 9:
            mtime = list(mtime)
            mtime[stat.ST_MTIME] = time.mktime(d)
            mtime = tuple(mtime)

    args['mtime'] = mtime
    return args


def get_metadata(lines):
    lines = list(lines)
    metadata = {}

    # pop the title
    lines.pop(0)
    while lines and lines[0].startswith('#'):
        meta = lines.pop(0)
        # remove the hash
        meta = meta[1:].strip()
        meta = meta.split(" ", 1)
        # if there's no value, we append a 1
        if len(meta) == 1:
            meta.append("1")
        metadata[meta[0].strip()] = meta[1].strip()

    return metadata


def cmd_persistdate(command, argv):
    import config

    datadir = config.py.get('datadir')

    if not datadir:
        raise ValueError('config.py has no datadir property.')

    from douglas import tools
    from douglas.app import Douglas

    p = Douglas(config.py, {})
    p.initialize()
    req = p.get_request()
    tools.run_callback('start', {'request': req})

    filelist = tools.get_entries(config, datadir)
    print '%d files' % len(filelist)
    for fn in filelist:
        lines = open(fn, 'r').readlines()
        try:
            metadata = get_metadata(lines)
        except IndexError as exc:
            print '%s errored out: %s' % (fn, exc)
            continue

        if 'published' in metadata:
            print '%s already has metadata...' % fn
            continue

        print 'working on %s...' % fn
        timetuple = tools.filestat(req, fn)
        published = time.strftime('%Y-%m-%d %H:%M:%S', timetuple)
        lines.insert(1, '#published %s\n' % published)
        fp = open(fn, 'w')
        fp.write(''.join(lines))
        fp.close()


def cb_commandline(args):
    args['persistdate'] = (
        cmd_persistdate, 'persists mtime of file into #published metadata')
    return args
