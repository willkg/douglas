"""
This is the default blosxom renderer.  It tries to match the behavior
of the blosxom renderer.
"""

import os
import sys

from douglas import tools
from douglas.renderers.base import RendererBase


class NoSuchThemeException(Exception):
    """
    This exception gets thrown when the theme requested is not
    available in this blog.
    """
    pass


def get_included_theme(taste):
    """
    douglas comes with themes in taste directories in the themes
    subdirectory of the douglas package.  This method pulls the template
    files for the associated taste (assuming it exists) or None if it
    doesn't.

    :param taste: The name of the taste.  e.g. "html", "rss", ...

    :returns: A dict of template type to template file or None
    """
    path = __file__[:__file__.rfind(os.sep)]
    path = path[:path.rfind(os.sep)+1] + "themes" + os.sep

    path = path + taste

    if os.path.isdir(path):
        template_files = os.listdir(path)
        template_d = {}
        for mem in template_files:
            name, ext = os.path.splitext(mem)
            if ext not in ["." + taste, ""] or name.startswith("."):
                continue
            template_d[name] = os.path.join(path, mem)
        return template_d

    return None


def get_theme_from_dir(path, taste):
    """
    Tries to get the template files for the theme of a certain
    taste (html, rss, atom10, ...) in a directory.  The files could
    be in the directory or in a taste subdirectory.

    :param path: the path of the directory to look for the theme
                 templates in

    :param taste: the theme files to look for (e.g. html, rss, atom10, ...)

    :returns: the map of template name to template file path
    """
    template_d = {}

    # if we have a taste directory, we check there
    if os.path.isdir(path + os.sep + taste):
        newpath = path + os.sep + taste
        template_files = os.listdir(newpath)
        for mem in template_files:
            name, ext = os.path.splitext(mem)
            if ext not in ["." + taste, ""]:
                continue
            template_d[name] = os.path.join(path + os.sep + taste, mem)
        return template_d

    # now we check the directory itself for theme templates
    template_files = os.listdir(path)
    for mem in template_files:
        if not mem.endswith("." + taste):
            continue
        template_d[os.path.splitext(mem)[0]] = path + os.sep + mem

    if template_d:
        return template_d

    return None


class BlosxomRenderer(RendererBase):
    """
    This is the default blosxom renderer.  It tries to match the behavior
    of the blosxom renderer.
    """
    def __init__(self, request, stdoutput=sys.stdout):
        RendererBase.__init__(self, request, stdoutput)
        config = request.get_configuration()
        self._request = request
        self.theme = None

    def get_parse_vars(self):
        """Returns a dict starting with standard filters, config
        information, then data information.  This allows vars
        to override each other correctly.  For example, plugins
        should be adding to the data dict which will override
        stuff in the config dict.
        """
        parsevars = dict(tools.STANDARD_FILTERS)
        parsevars.update(self._request.config)
        parsevars.update(self._request.data)
        return parsevars

    def get_theme(self, taste='html'):
        """
        This retrieves all the template files for a given theme
        taste.  This will first pull the templates for the default
        theme of this taste if there are any.  Then it looks at
        EITHER the configured datadir OR the themedir (if
        configured).  It'll go through directories overriding the
        template files it has already picked up descending the
        category path of the douglas request.

        For example, if the user requested the ``html`` theme and is
        looking at an entry in the category ``dev/douglas``, then
        ``get_theme`` will:

        1. pick up the theme files in the default html theme
        2. start in EITHER datadir OR themedir (if configured)
        3. override the default html theme files with html theme
           files in this directory or in ``html/`` subdirectory
        4. override the html theme files it's picked up so far
           with html files in ``dev/`` or ``dev/html/``
        5. override the html theme files it's picked up so far
           with html files in ``dev/douglas/`` or
           ``dev/douglas/html/``

        If it doesn't find any theme files at all, then it returns
        None which indicates the theme doesn't exist in this blog.

        :param taste: the taste to retrieve theme files for.

        :returns: mapping of template name to template file data
        """
        data = self._request.get_data()
        config = self._request.get_configuration()
        datadir = config["datadir"]

        # if they have themedir set, then we look there.  otherwise
        # we look in the datadir.
        themedir = config.get("themedir", datadir)

        # first we grab the theme files for the included theme (if
        # we have one).
        template_d = get_included_theme(taste)
        if not template_d:
            template_d = {}

        pathinfo = list(data["path_info"])

        # check the root of themedir for templates
        new_files = get_theme_from_dir(themedir, taste)
        if new_files:
            template_d.update(new_files)

        # go through all the directories from the themedir all
        # the way up to the root_datadir.  this way template files
        # can override template files in parent directories.
        while len(pathinfo) > 0:
            themedir = os.path.join(themedir, pathinfo.pop(0))
            if os.path.isfile(themedir):
                break

            if not os.path.isdir(themedir):
                break

            new_files = get_theme_from_dir(themedir, taste)
            if new_files:
                template_d.update(new_files)

        # if we still haven't found our theme files, we raise an exception
        if not template_d:
            raise NoSuchThemeException("Theme '%s' does not exist." % taste)

        for k in template_d.keys():
            template_d[k] = open(template_d[k]).read()

        return template_d

    def render_content(self, content):
        """
        Processes the content for the story portion of a page.

        :param content: the content to be rendered

        :returns: the content string
        """
        data = self._request.get_data()

        outputbuffer = []

        if callable(content):
            # if the content is a callable function, then we just spit out
            # whatever it returns as a string
            outputbuffer.append(content())

        elif isinstance(content, dict):
            # if the content is a dict, then we parse it as if it were an
            # entry--except it's distinctly not an EntryBase derivative
            var_dict = self.get_parse_vars()
            var_dict.update(content)

            output = tools.parse(self._request, var_dict, self.theme['story'])
            outputbuffer.append(output)

        elif isinstance(content, list):
            if len(content) > 0:
                current_date = content[0]["date"]

                if current_date and "date_head" in self.theme:
                    parse_vars = self.get_parse_vars()
                    parse_vars.update({"date": current_date,
                                       "yr": content[0]["yr"],
                                       "mo": content[0]["mo"],
                                       "da": content[0]["da"]})
                    outputbuffer.append(
                        self.render_template(parse_vars, "date_head"))

                for entry in content:
                    if entry["date"] and entry["date"] != current_date:
                        if "date_foot" in self.theme:
                            parse_vars = self.get_parse_vars()
                            parse_vars.update({"date": current_date,
                                               "yr": content[0]["yr"],
                                               "mo": content[0]["mo"],
                                               "da": content[0]["da"]})

                            outputbuffer.append(
                                self.render_template(parse_vars, "date_foot"))

                        if "date_head" in self.theme:
                            current_date = entry["date"]
                            parse_vars = self.get_parse_vars()
                            parse_vars.update({"date": current_date,
                                               "yr": content[0]["yr"],
                                               "mo": content[0]["mo"],
                                               "da": content[0]["da"]})
                            outputbuffer.append(
                                self.render_template(parse_vars, "date_head"))

                    if data['content-type'] == 'text/plain':
                        s = tools.Stripper()
                        s.feed(entry.get_data())
                        s.close()
                        p = ['  ' + line for line in s.gettext().split('\n')]
                        entry.set_data('\n'.join(p))

                    parse_vars = self.get_parse_vars()
                    parse_vars.update(entry)

                    outputbuffer.append(
                        self.render_template(parse_vars, "story", override=1))

                    args = {"entry": parse_vars, "template": ""}
                    args = self._run_callback("story_end", args)
                    outputbuffer.append(args["template"])

                if current_date and "date_foot" in self.theme:
                    parse_vars = self.get_parse_vars()
                    parse_vars.update({"date": current_date})
                    outputbuffer.append(
                        self.render_template(parse_vars, "date_foot"))

        return outputbuffer

    renderContent = tools.deprecated_function(render_content)

    def render(self, header=True):
        """
        Figures out themes and such and then renders the content according
        to which theme we're using.

        :param header: whether (True) or not (False) to render the HTTP headers
        """
        # if we've already rendered, then we don't want to do so again
        if self.rendered:
            return

        data = self._request.get_data()

        try:
            theme = data.get("theme") or "html"
            self.theme = self.get_theme(theme)

        except NoSuchThemeException as nsfe:
            error_msg = str(nsfe)
            try:
                self.theme = self.get_theme("error")
            except NoSuchThemeException:
                self.theme = get_included_theme("error")
                error_msg += "  And your error theme doesn't exist, either."

            resp = self._request.get_response()
            resp.set_status("404 Not Found")
            self._content = {"title": "HTTP 404: Theme error",
                             "body": error_msg}

        data['content-type'] = self.theme['content_type'].strip()
        if header:
            if self._needs_content_type and data['content-type'] != "":
                self.add_header('Content-type', '%(content-type)s' % data)

            self.show_headers()

        if self._content:
            if "head" in self.theme:
                self.write(self.render_template(self.get_parse_vars(), "head"))
            if "story" in self.theme:
                content = self.render_content(self._content)
                for i, mem in enumerate(content):
                    if isinstance(mem, unicode):
                        content[i] = mem.encode("utf-8")
                content = "".join(content)
                self.write(content)
            if "foot" in self.theme:
                self.write(self.render_template(self.get_parse_vars(), "foot"))

        self.rendered = 1

    def render_template(self, entry, template_name, override=0):
        """
        Find the theme template for template_name, run any blosxom
        callbacks, substitute entry into it and render the template.

        If the entry has a ``template_name`` property and override is
        True (this happens in the story template), then we'll use that
        template instead.

        :param entry: the entry/variable-dict to use for expanding variables

        :param template_name: template name (gets looked up in self.theme)

        :param override: whether (True) or not (False) this template can
            be overriden with the ``template_name`` value in the entry
        """
        template = ""
        if override:
            # here we do a quick override...  if the entry has a
            # template field we use that instead of the template_name
            # argument passed in.
            actual_template_name = entry.get("template_name", template_name)
            template = self.theme.get(actual_template_name, '')

        if not template:
            template = self.theme.get(template_name, '')

        # we run this through the regular callbacks
        args = self._run_callback(template_name,
                                  {"entry": entry, "template": template})

        template = args["template"]

        # FIXME - the finaltext.replace(...) below causes \$ to get
        # unescaped in title and body text which is wrong.  this
        # fix alleviates that somewhat, but there are still edge
        # cases regarding function data.  need a real template
        # engine with a real parser here.
        entry = dict(args["entry"])
        for k, v in entry.items():
            if isinstance(v, basestring):
                entry[k] = v.replace(r"\$", r"\\$")

        finaltext = tools.parse(self._request, entry, template)
        return finaltext.replace(r'\$', '$')

    renderTemplate = tools.deprecated_function(render_template)

    def _run_callback(self, chain, input):
        """
        Makes calling blosxom callbacks a bit easier since they all
        have the same mechanics.  This function merely calls
        run_callback with the arguments given and a mappingfunc.

        The mappingfunc copies the ``template`` value from the output to
        the input for the next function.

        Refer to run_callback for more details.
        """
        input.update({"renderer": self})
        input.update({"request": self._request})

        return tools.run_callback(chain, input,
                                  mappingfunc=lambda x,y: x,
                                  defaultfunc=lambda x:x)

    def output_template(self, output, entry, template_name):
        """
        Deprecated.  Here for backwards compatibility.
        """
        output.append(self.render_template(entry, template_name))

    outputTemplate = tools.deprecated_function(output_template)

class Renderer(BlosxomRenderer):
    pass
