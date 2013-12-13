"""
This is the debug renderer.  This is very useful for debugging plugins
and templates.
"""

import os

from douglas.renderers.base import RendererBase
from douglas import tools, plugin_utils


HBAR = ('-' * 70) + '\n'


def escv(s):
    """
    Takes in a value.  If it's not a string, we repr it and turn it into
    a string.  Then we escape it so it can be printed in HTML safely.

    :param s: any value

    :returns: a safe-to-print-in-html string representation of the value
    """
    if not s:
        return ""

    if not isinstance(s, str):
        s = repr(s)

    return tools.escape_text(s)

class Renderer(RendererBase):
    """
    This is the debug renderer.  This is very useful for debugging
    plugins and templates.
    """
    def print_map(self, keymap):
        """
        Takes a map of keys to values and applies the function f to a pretty
        printed version of each key/value pair.

        :param printfunc: function for printing

        :param keymap: a mapping of key/value pairs
        """
        keys = keymap.keys()
        keys.sort()
        for key in keys:
            self.write("<font color=\"#0000ff\">%s</font> -&gt; %s\n" % \
                       (escv(key), escv(keymap[key])))

    def print_section(self, title, section=None):
        self.write(HBAR)
        self.write(title + '\n')
        self.write(HBAR)
        if section:
            self.print_map(section)

    def render(self, render_headers=True):
        """
        Renders a douglas request after we've gone through all the
        motions of converting data and getting entries to render.

        :arg render_headers: either prints (True) or does not print (True)
            the http headers.
        """
        pyhttp = self._request.get_http()
        config = self._request.get_configuration()
        data = self._request.get_data()
        printout = self.write

        if render_headers:
            self.add_header('Content-type', 'text/html')
            self.show_headers()

        printout("<html>")
        printout("<body>")
        printout("<pre>")
        printout("Welcome to debug mode!\n")
        printout("You requested the %(theme)s theme.\n" % data)

        self.print_section('HTTP return headers:')
        for k, v in self._header:
            printout("<font color=\"#0000ff\">%s</font> -&gt; %s\n" % \
                     (escv(k), escv(v)))

        self.print_section('The OS environment contains:', os.environ)

        self.print_section('Plugins:')
        printout("Plugins that loaded:\n")
        if plugin_utils.plugins:
            for plugin in plugin_utils.plugins:
                printout(" * " + escv(plugin) + "\n")
        else:
            printout("None\n")

        printout("\n")

        printout("Plugins that didn't load:\n")
        if plugin_utils.bad_plugins:
            for plugin, exc in plugin_utils.bad_plugins:
                exc = "    " + "\n    ".join(exc.splitlines()) + "\n"
                printout(" * " + escv(plugin) + "\n")
                printout(escv(exc))
        else:
            printout("None\n")

        self.print_section('Request.get_http() dict contains:', pyhttp)
        self.print_section('Request.get_configuration() dict contains:', config)
        self.print_section('Request.get_data() dict contains:', data)

        self.print_section('Entries to process:')
        for content in self._content:
            if not isinstance(content, str):
                printout("%s\n" %
                         escv(content.get('filename', 'No such file\n')))

        self.print_section('Entries processed:')
        for content in self._content:
            if not isinstance(content, str):
                printout(HBAR)
                emsg = escv(content.get('filename', 'No such file\n'))
                printout("Items for %s:\n" % emsg)
                printout(HBAR)
                self.print_map(content)

        printout(HBAR)

        printout("</body>")
        printout("</html>")
