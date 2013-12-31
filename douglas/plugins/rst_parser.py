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


Configuration
=============

There's two optional configuration parameter you can for additional
control over the rendered HTML::

   # To set the starting level for the rendered heading elements.
   # 1 is the default.
   py['reST_initial_header_level'] = 1

   # Enable or disable the promotion of a lone top-level section title to
   # document title (and subsequent section title to document subtitle
   # promotion); disabled by default.
   py['reST_transform_doctitle'] = 0


.. Note::

   If you're not seeing headings that you think should be there, try
   changing the ``reST_initial_header_level`` property to 0.


Usage
=====

Blog entries with a ``.rst`` extension will be parsed as
reStructuredText.

Blog entries can have a summary. Insert a break directive at the point
where the summary should end. For example::

    First part of my blog entry....

    .. break::

    Second part of my blog entry after the fold.

Some entries don't have a summary attribute, so if you're going to
show the summary, you need to make sure it's defined first.

For example, in your entry_list template, you could show the summary
like this::

    {% if entry.summary is defined %}
      {{ entry.summary|safe }}
      <p><a href="{{ entry.url }}">Read more...</a></p>
    {% else %}
      {{ entry.body|safe }}
    {% endif %}

"""

__description__ = "restructured text support for blog entries"
__category__ = "text"
__license__ = "MIT"


from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst import directives, Directive

from douglas import tools
from douglas.memcache import memcache_decorator


FILE_EXT = 'rst'


# READMORE_BREAKPOINT = 'BREAKLIKEYOUMEANIT!'
# class Break(Directive):
#     """
#     Transform a break directive (".. break::") into the text that the
#     Pyblosxom readmore plugin looks for.  This allows blog entries to
#     have a "summary" section for long blog entries.

#     """
#     required_arguments = 0
#     optional_arguments = 0
#     final_argument_whitespace = True
#     has_content = False

#     def run(self):
#         return [nodes.raw('', READMORE_BREAKPOINT + '\n', format='html')]

# directives.register_directive('break', Break)


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


def parse(body, request):
    cfg = request.get_configuration()
    initial_header_level = cfg.get('reST_initial_header_level', 1)
    transform_doctitle = cfg.get('reST_transform_doctitle', 0)

    return _parse(initial_header_level, transform_doctitle, body)


def parse_rst_file(filename, request):
    cfg = request.get_configuration()
    entry_data = dict(tools.parse_entry_file(filename, cfg['blog_encoding']))
    body = entry_data['body']

    if '.. break::' in body:
        entry_data['body'] = parse(body.replace('.. break::', ''), request)
        entry_data['summary'] = parse(body[:body.find('.. break::')], request)
    else:
        entry_data['body'] = parse(body, request)

    return entry_data


def cb_entryparser(args):
    args[FILE_EXT] = parse_rst_file
    return args
