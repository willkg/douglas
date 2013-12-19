"""
Summary
=======

A reStructuredText entry formatter for douglas.  reStructuredText is
part of the docutils project (http://docutils.sourceforge.net/).  To
use, you need a *recent* version of docutils.  A development snapshot
(http://docutils.sourceforge.net/#development-snapshots) will work
fine.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.rst_parser`` to the ``load_plugins`` list
   in your ``config.py`` file.

2. Install docutils.  Instructions are at
   http://docutils.sourceforge.net/


Usage
=====

Blog entries with a ``.rst`` extension will be parsed as
restructuredText.

You can also configure this as your default preformatter for ``.txt``
files by configuring it in your config file as follows::

   py['parser'] = 'reST'

Additionally, you can do this on an entry-by-entry basis by adding a
``#parser reST`` line in the metadata section.  For example::

   My Little Blog Entry
   #parser reST
   My main story...


Additionally, blog entries can have a summary. Insert a break directive
at the point where the summary should end. For example::

    First part of my blog entry....

    .. break::

    Secon part of my blog entry after the fold.


Configuration
=============

There's two optional configuration parameter you can for additional
control over the rendered HTML::

   # To set the starting level for the rendered heading elements.
   # 1 is the default.
   py['reST_initial_header_level'] = 1

   # Enable or disable the promotion of a lone top-level section title to
   # document title (and subsequent section title to document subtitle
   # promotion); enabled by default.
   py['reST_transform_doctitle'] = 1


.. Note::

   If you're not seeing headings that you think should be there, try
   changing the ``reST_initial_header_level`` property to 0.

"""

__description__ = "restructured text support for blog entries"
__category__ = "text"
__license__ = "MIT"


from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst import directives, Directive

from douglas import tools
from douglas.memcache import memcache_decorator


PREFORMATTER_ID = 'reST'
FILE_EXT = 'rst'
READMORE_BREAKPOINT = 'BREAKLIKEYOUMEANIT!'


class Break(Directive):
    """
    Transform a break directive (".. break::") into the text that the
    Pyblosxom readmore plugin looks for.  This allows blog entries to
    have a "summary" section for long blog entries.

    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        return [nodes.raw('', READMORE_BREAKPOINT + '\n', format='html')]

directives.register_directive('break', Break)


def cb_entryparser(args):
    args[FILE_EXT] = readfile
    return args


def cb_preformat(args):
    if args.get("parser", None) == PREFORMATTER_ID:
        return parse(''.join(args['story']), args['request'])


@memcache_decorator('rst_parser')
def _parse(initial_header_level, transform_doctitle, story):
    parts = publish_parts(
        story,
        writer_name='html',
        settings_overrides={
            'initial_header_level': initial_header_level,
            'doctitle_xform': transform_doctitle,
            'syntax_highlight': 'short'
            })
    return parts['body']


def parse(story, request):
    config = request.getConfiguration()
    initial_header_level = config.get('reST_initial_header_level', 1)
    transform_doctitle = config.get('reST_transform_doctitle', 1)

    return _parse(initial_header_level, transform_doctitle, story)


def readfile(filename, request):
    entry_data = {}
    with open(filename, 'r') as fp:
        lines = fp.readlines()

    if len(lines) == 0:
        return {'title': '', 'summary': '', 'body': ''}

    title = lines.pop(0).strip()

    # absorb meta data
    while lines and lines[0].startswith("#"):
        meta = lines.pop(0)
        # remove the hash
        meta = meta[1:].strip()
        meta = meta.split(" ", 1)
        # if there's no value, we append a 1
        if len(meta) == 1:
            meta.append("1")
        entry_data[meta[0].strip()] = meta[1].strip()

    body = parse(''.join(lines), request)
    entry_data["title"] = title

    body = body.split(READMORE_BREAKPOINT)

    if len(body) > 1:
        entry_data['summary'] = body[0]
    else:
        entry_data['summary'] = ''
    entry_data['body'] = ''.join(body)

    # Call the postformat callbacks
    tools.run_callback('postformat', {'request': request,
                                      'entry_data': entry_data})
    return entry_data
