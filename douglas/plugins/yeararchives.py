"""
Summary
=======

Walks through your blog root figuring out all the available years for
the archives list.  It stores the years with links to year summaries
in the variable ``$(archivelinks)``.  You should put this variable in
either your head or foot template.


Install
=======

This plugin comes with Douglas.  To install, do the following:

1. Add ``douglas.plugins.yeararchives`` to the ``load_plugins`` list
   in your ``config.py`` file.

2. Add ``$(archivelinks)`` to your head and/or foot templates.

3. Configure as documented below.


Usage
=====

When the user clicks on one of the year links
(e.g. ``http://base_url/2004/``), then yeararchives will display a
summary page for that year.  The summary is generated using the
``yearsummarystory`` template for each month in the year.

My ``yearsummarystory`` template looks like this::

   <div class="blosxomEntry">
   <span class="blosxomTitle">$title</span>
   <div class="blosxomBody">
   <table>
   $body
   </table>
   </div>
   </div>


The ``$(archivelinks)`` link can be configured with the
``archive_template`` config variable.  It uses the Python string
formatting syntax.

Example::

    py['archive_template'] = (
        '<a href="%(base_url)s/%(Y)s/index.%(f)s">'
        '%(Y)s</a><br />')

The vars available with typical example values are::

    Y      4-digit year   ex: '1978'
    y      2-digit year   ex: '78'
    f      the theme    ex: 'html'

.. Note::

   The ``archive_template`` variable value is formatted using Python
   string formatting rules--not Douglas template rules!

"""

__description__ = "Builds year-based archives listing."
__category__ = "archives"
__license__ = "MIT"


from douglas import tools, entries
from douglas.memcache import memcache_decorator
from douglas.tools import pwrap
import time


def verify_installation(cfg):
    if not 'archive_template' in cfg:
        pwrap(
            "missing optional config property 'archive_template' which "
            "allows you to specify how the archive links are created.  "
            "refer to yeararchives plugin documentation for more details.")

    return True


class YearArchives:
    def __init__(self, request):
        self._request = request
        self._archives = None
        self._items = None

    @memcache_decorator('yeararchives', True)
    def __str__(self):
        if self._archives == None:
            self.gen_linear_archive()
        return self._archives

    def gen_linear_archive(self):
        config = self._request.get_configuration()
        data = self._request.get_data()
        root = config["datadir"]

        archives = {}
        archive_list = tools.get_entries(config, root)
        items = []

        fulldict = {}
        fulldict.update(config)
        fulldict.update(data)

        theme = data.get(
            "theme", config.get("default_theme", "html"))

        template = config.get(
            'archive_template',
            '<a href="%(base_url)s/%(Y)s/index.%(f)s">%(Y)s</a><br />')

        for mem in archive_list:
            timetuple = tools.filestat(self._request, mem)

            timedict = {}
            for x in ["m", "Y", "y", "d"]:
                timedict[x] = time.strftime("%" + x, timetuple)

            fulldict.update(timedict)
            fulldict["f"] = theme
            year = fulldict["Y"]

            if not year in archives:
                archives[year] = template % fulldict
            items.append(
                ["%(Y)s-%(m)s" % fulldict,
                 "%(Y)s-%(m)s-%(d)s" % fulldict,
                 time.mktime(timetuple),
                 mem])

        arc_keys = sorted(archives.keys(), reverse=True)

        result = []
        for key in arc_keys:
            result.append(archives[key])
        self._archives = '\n'.join(result)
        self._items = items


def new_entry(request, yearmonth, body):
    """
    Takes a bunch of variables and generates an entry out of it.  It
    creates a timestamp so that conditionalhttp can handle it without
    getting all fussy.
    """
    entry = entries.base.EntryBase(request)

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


INIT_KEY = "yeararchives_initiated"


def cb_prepare(args):
    request = args["request"]
    data = request.get_data()
    data["archivelinks"] = YearArchives(request)


def cb_date_head(args):
    request = args["request"]
    data = request.get_data()

    if INIT_KEY in data:
        args["template"] = ""
    return args


def parse_path_info(path):
    """Returns None or (year, theme) tuple.

    Handles urls of this type:

    - /2003
    - /2003/
    - /2003/index
    - /2003/index.theme
    """
    path = path.split("/")
    path = [m for m in path if m]
    if not path:
        return

    year = path[0]
    if not year.isdigit() or not len(year) == 4:
        return

    if len(path) == 1:
        return (year, None)

    if len(path) == 2 and path[1].startswith("index"):
        theme = None
        if "." in path[1]:
            theme = path[1].split(".", 1)[1]
        return (year, theme)

    return


def cb_filelist(args):
    request = args["request"]
    pyhttp = request.get_http()
    data = request.get_data()
    config = request.get_configuration()
    baseurl = config.get("base_url", "")

    path = pyhttp["PATH_INFO"]

    ret = parse_path_info(path)
    if ret == None:
        return

    # note: returned theme is None if there is no .theme appendix
    year, theme = ret

    data[INIT_KEY] = 1

    # get all the entries
    wa = YearArchives(request)
    wa.gen_linear_archive()
    items = wa._items

    # peel off the items for this year
    items = sorted([m for m in items if m[0].startswith(year)], reverse=True)

    # Set and use current (or default) theme for permalinks
    if not theme:
        theme = data.get(
            "theme", config.get("default_theme", "html"))

    data["theme"] = theme

    l = ("(%(path)s) <a href=\"" + baseurl +
         "/%(file_path)s." + theme + "\">%(title)s</a><br>")
    e = "<tr>\n<td valign=\"top\" align=\"left\">%s</td>\n<td>%s</td></tr>\n"
    d = ""
    m = ""

    day = []
    month = []
    entrylist = []

    for mem in items:
        if not m:
            m = mem[0]
        if not d:
            d = mem[1]

        if m != mem[0]:
            month.append(e % (d, "\n".join(day)))
            entrylist.append(new_entry(request, m, "\n".join(month)))
            m = mem[0]
            d = mem[1]
            day = []
            month = []

        elif d != mem[1]:
            month.append(e % (d, "\n".join(day)))
            d = mem[1]
            day = []
        entry = entries.fileentry.FileEntry(
            request, mem[3], config['datadir'])
        day.append(l % entry)

    if day:
        month.append(e % (d, "\n".join(day)))
    if month:
        entrylist.append(new_entry(request, m, "\n".join(month)))

    return entrylist
