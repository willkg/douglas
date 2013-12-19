"""
Summary
=======

Walks through your blog root figuring out all the available years for
the archives list.  Handles year-based indexes.  Builds a list of years
your blog has entries for which you can use in your template.


Install
=======

This plugin comes with Douglas.  To install, do the following:

1. Add ``douglas.plugins.yeararchives`` to the ``load_plugins`` list
   in your ``config.py`` file.


Usage
=====

Add::

    {{ yeararchives.as_list()|safe }}

to the appropriate place in your template.

When the user clicks on one of the year links (e.g.
``http://example.com/2004/``), then yeararchives will display a
summary page for that year.

"""

__description__ = "Builds year-based archives listing."
__category__ = "archives"
__license__ = "MIT"


import re
import time

from douglas import tools
from douglas.app import blosxom_truncate_list_handler
from douglas.entries.base import EntryBase
from douglas.entries.fileentry import FileEntry


class YearArchivesManager(object):
    def __init__(self, request):
        self.request = request
        self._entries = None

    @property
    def entries(self):
        """List of (year, entry) tuples"""
        if self._entries is None:
            cfg = self.request.get_configuration()
            entry_list = tools.get_entries(cfg, cfg['datadir'])
            self._entries = []
            for mem in entry_list:
                timetuple = tools.filestat(self.request, mem)
                self._entries.append(
                    (time.strftime('%Y', timetuple),
                     time.strftime('%Y-%m', timetuple),
                     time.strftime('%Y-%m-d', timetuple),
                     mem))

        return self._entries

    def as_list(self):
        config = self.request.get_configuration()
        data = self.request.get_data()

        item_t = '<li><a href="{baseurl}/{year}/index.{theme}">{year}</a></li>'
        theme = data.get('theme', config.get('default_theme', 'html'))

        years = set([mem[0] for mem in self.entries])

        output = []
        output.append('<ul class="yearArchives">')

        for year in sorted(years):
            output.append(item_t.format(
                baseurl=config.get('base_url', ''),
                year=year,
                theme=theme))
        output.append('</ul>')

        return '\n'.join(output)


def new_entry(request, yearmonth, body):
    """
    Takes a bunch of variables and generates an entry out of it.  It
    creates a timestamp so that conditionalhttp can handle it without
    getting all fussy.
    """
    entry = EntryBase(request)

    entry['title'] = yearmonth
    entry['filename'] = yearmonth + "/summary"
    entry['file_path'] = yearmonth
    entry._id = yearmonth + "::summary"

    entry["template_name"] = "yearsummarystory"
    entry["nocomments"] = "yes"

    entry["absolute_path"] = ""
    entry["fn"] = ""

    entry.set_time(time.strptime(yearmonth, "%Y-%m"))
    entry['body'] = body

    return entry


def cb_context_processor(args):
    context = args['context']
    request = args['request']
    context['yeararchives'] = YearArchivesManager(request)
    return args


def parse_path_info(path):
    """Returns None or (year, theme) tuple.

    Handles urls of this type:

    - /2003
    - /2003/
    - /2003/index
    - /2003/index.theme
    """
    match = re.match(r'^/(\d{4})(/index.*)?', path)
    if not match:
        return

    year, index_theme = match.groups()

    # If there's no "index.foo" part, then we don't know the theme, so
    # return None for the theme.
    if index_theme and '.' in index_theme:
        return (year, index_theme.split('.', 1)[1])

    return (year, None)


# FIXME - probably want to switch the template
def cb_filelist(args):
    request = args['request']
    pyhttp = request.get_http()
    data = request.get_data()
    cfg = request.get_configuration()
    baseurl = cfg.get('base_url', '')

    path = pyhttp['PATH_INFO']

    ret = parse_path_info(path)
    if ret == None:
        return

    # Note: returned theme is None if there is no .theme appendix
    year, theme = ret

    # Get all the entries for this year
    yeararchives = YearArchivesManager(request)
    items = sorted([mem for mem in yeararchives.entries
                    if mem[0] == year], reverse=True)

    # Set and use current (or default) theme for permalinks
    if not theme:
        theme = data.get('theme', cfg.get('default_theme', 'html'))

    data['theme'] = theme

    item_t = '({path}) <a href="{baseurl}/{file_path}.{theme}">{title}</a><br>'
    e = "<tr>\n<td valign=\"top\" align=\"left\">%s</td>\n<td>%s</td></tr>\n"

    current_month = items[0][1]
    current_day = items[0][2]

    day = []
    month = []
    entrylist = []

    for mem in items:
        if current_month != mem[1]:
            month.append(e % (current_day, '\n'.join(day)))
            entrylist.append(
                new_entry(
                    request,
                    current_month,
                    '<table>' + '\n'.join(month) + '</table>'))
            current_month = mem[1]
            current_day = mem[2]
            day = []
            month = []

        elif current_day != mem[2]:
            month.append(e % (current_day, '\n'.join(day)))
            current_day = mem[2]
            day = []

        entry = FileEntry(request, mem[3], cfg['datadir'])
        entry.update({
            'baseurl': baseurl,
            'theme': theme
        })

        day.append(item_t.format(**entry))

    if day:
        month.append(e % (current_day, '\n'.join(day)))

    if month:
        entrylist.append(
            new_entry(
                request,
                current_month,
                '<table>' + '\n'.join(month) + '</table>'))

    return entrylist
