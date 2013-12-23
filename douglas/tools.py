import HTMLParser
import logging
import os
import os.path
import random
import re
import shutil
import stat
import string
import sys
import textwrap
import time
import urllib
from urlparse import urlparse, urlsplit, urlunsplit

from douglas import plugin_utils


MONTHS = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
]


def pwrap(s):
    """Wraps the text and prints it.
    """
    starter = ""
    linesep = os.linesep
    if s.startswith("- "):
        starter = "- "
        s = s[2:]
        linesep = os.linesep + "  "

    print starter + linesep.join(textwrap.wrap(s, 72))


def pwrap_error(s):
    """Wraps an error message and prints it to stderr.
    """
    starter = ""
    linesep = os.linesep
    if s.startswith("- "):
        starter = "- "
        s = s[2:]
        linesep = os.linesep + "  "

    sys.stderr.write(starter + linesep.join(textwrap.wrap(s, 72)) + "\n")


def abort(msg):
    pwrap_error(msg)
    pwrap_error("Exiting.")
    return 1


class ConfigSyntaxErrorException(Exception):
    """Thrown when ``convert_configini_values`` encounters a syntax
    error.
    """
    pass


def convert_configini_values(configini):
    """Takes a dict containing config.ini style keys and values, converts
    the values, and returns a new config dict.

    :param confini: dict containing the config.ini style keys and values

    :raises ConfigSyntaxErrorException: when there's a syntax error

    :returns: new config dict
    """
    def s_or_i(text):
        """
        Takes a string and if it begins with \" or \' and ends with
        \" or \', then it returns the string.  If it's an int, returns
        the int.  Otherwise it returns the text.
        """
        text = text.strip()
        if (((text.startswith('"') and not text.endswith('"'))
             or (not text.startswith('"') and text.endswith('"')))):
            raise ConfigSyntaxErrorException(
                "config syntax error: string '%s' missing start or end \"" %
                text)
        elif (((text.startswith("'") and not text.endswith("'"))
               or (not text.startswith("'") and text.endswith("'")))):
            raise ConfigSyntaxErrorException(
                "config syntax error: string '%s' missing start or end '" %
                text)
        elif text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        elif text.startswith("'") and text.endswith("'"):
            return text[1:-1]
        elif text.isdigit():
            return int(text)
        return text

    config = {}
    for key, value in configini.items():
        # in configini.items, we pick up a local_config which seems
        # to be a copy of what's in configini.items--puzzling.
        if isinstance(value, dict):
            continue

        value = value.strip()
        if (((value.startswith("[") and not value.endswith("]"))
             or (not value.startswith("[") and value.endswith("]")))):
            raise ConfigSyntaxErrorException(
                "config syntax error: list '%s' missing [ or ]" %
                value)
        elif value.startswith("[") and value.endswith("]"):
            value2 = value[1:-1].strip().split(",")
            if len(value2) == 1 and value2[0] == "":
                # handle the foo = [] case
                config[key] = []
            else:
                config[key] = [s_or_i(s.strip()) for s in value2]
        else:
            config[key] = s_or_i(value)

    return config


def parse_entry_file(filename):
    """Parses a a Douglas-structured entry file"""
    entry_data = {}
    with open(filename, 'r') as fp:
        lines = fp.readlines()

    if not lines:
        return {'title': '', 'body': ''}

    entry_data['title'] = lines.pop(0).strip()

    while lines and lines[0].startswith('#'):
        meta = lines.pop(0)
        match = re.match(r'^#([^\s]+)( [^$]+)?$', meta)
        key, val = match.groups()
        entry_data[key.strip()] = val.strip() if (val and val.strip()) else '1'

    entry_data['body'] = ''.join(lines)
    return entry_data


def escape_text(s):
    """Takes in a string and converts:

    * ``&`` to ``&amp;``
    * ``>`` to ``&gt;``
    * ``<`` to ``&lt;``
    * ``\"`` to ``&quot;``
    * ``'`` to ``&#x27;``
    * ``/`` to ``&#x2F;``

    Note: if ``s`` is ``None``, then we return ``None``.

    >>> escape_text(None)
    None
    >>> escape_text("")
    ""
    >>> escape_text("a'b")
    "a&#x27;b"
    >>> escape_text('a"b')
    "a&quot;b"
    """
    if not s:
        return s

    for mem in (("&", "&amp;"), (">", "&gt;"), ("<", "&lt;"), ("\"", "&quot;"),
                ("'", "&#x27;"), ("/", "&#x2F;")):
        s = s.replace(mem[0], mem[1])
    return s


def urlencode_text(s):
    """Calls ``urllib.quote`` on the string ``s``.

    Note: if ``s`` is ``None``, then we return ``None``.

    >>> urlencode_text(None)
    None
    >>> urlencode_text("")
    ""
    >>> urlencode_text("a c")
    "a%20c"
    >>> urlencode_text("a&c")
    "a%26c"
    >>> urlencode_text("a=c")
    "a%3Dc"

    """
    if not s:
        return s

    return urllib.quote(s)


def get_entries(cfg, root, recurse=0):
    """Returns a list of all the entries in the root

    This only pulls extensions that are registered with entryparsers.
    This uses the ``entries`` callback.

    Allows plugins to remove and add items.

    FIXME - fix docs

    """
    # the root must be a directory
    if not os.path.isdir(root):
        return []

    ext = cfg.get('extensions', {})
    pattern = re.compile(r'.*\.(' + '|'.join(ext.keys()) + r')$')

    ignore = cfg.get("ignore_directories", None)
    if isinstance(ignore, basestring):
        ignore = [ignore]

    if ignore:
        ignore = [re.escape(i) for i in ignore]
        ignorere = re.compile(r'.*?(' + '|'.join(ignore) + r')$')
    else:
        ignorere = None

    entry_files = _walk_internal(root, recurse, pattern, ignorere, 0)
    argdict = {
        'config': cfg,
        'entry_files': entry_files
    }

    # FIXME - this callback name sucks.
    argdict = run_callback(
        'entries',
        argdict,
        mappingfunc=lambda x, y: y,
        defaultfunc=lambda x: x)

    return argdict['entry_files']


def walk(request, root='.', recurse=0, pattern='', return_folders=0):
    """
    This function walks a directory tree starting at a specified root
    folder, and returns a list of all of the files (and optionally
    folders) that match our pattern(s). Taken from the online Python
    Cookbook and modified to own needs.

    It will look at the config "ignore_directories" for a list of
    directories to ignore.  It uses a regexp that joins all the things
    you list.  So the following::

       config.py["ignore_directories"] = ["CVS", "dev/douglas"]

    turns into the regexp::

       .*?(CVS|dev/douglas)$

    It will also skip all directories that start with a period.

    :param request: Request
    :param root: the root directory to walk
    :param recurse: the depth of recursion; defaults to 0 which goes all
                    the way down
    :param pattern: the regexp object for matching files; defaults to
                    '' which causes douglas to return files with
                    file extensions that match those the entryparsers
                    handle
    :param return_folders: True if you want only folders, False if you
                    want files AND folders

    :returns: a list of file paths.
    """
    # expand pattern
    if not pattern:
        ext = request.get_configuration()['extensions']
        pattern = re.compile(r'.*\.(' + '|'.join(ext.keys()) + r')$')

    ignore = request.get_configuration().get("ignore_directories", None)
    if isinstance(ignore, str):
        ignore = [ignore]

    if ignore:
        ignore = [re.escape(i) for i in ignore]
        ignorere = re.compile(r'.*?(' + '|'.join(ignore) + r')$')
    else:
        ignorere = None

    # must have at least root folder
    if not os.path.isdir(root):
        return []

    return _walk_internal(root, recurse, pattern, ignorere, return_folders)


def _walk_internal(root, recurse, pattern, ignorere, return_folders):
    """
    Note: This is an internal function--don't use it and don't expect
    it to stay the same between Douglas releases.
    """
    # FIXME - we should either ditch this function and use os.walk or
    # something similar, or optimize this version by removing the
    # multiple stat calls that happen as a result of islink, isdir and
    # isfile.

    # initialize
    result = []

    try:
        names = os.listdir(root)
    except OSError:
        return []

    # check each file
    for name in names:
        fullname = os.path.normpath(os.path.join(root, name))

        # grab if it matches our pattern and entry type
        if pattern.match(name):
            if ((os.path.isfile(fullname) and not return_folders) or
                (return_folders and os.path.isdir(fullname) and
                 (not ignorere or not ignorere.match(fullname)))):
                result.append(fullname)

        # recursively scan other folders, appending results
        if (recurse == 0) or (recurse > 1):
            if ((name[0] != "." and os.path.isdir(fullname)
                 and not os.path.islink(fullname)
                 and (not ignorere or not ignorere.match(fullname)))):
                result = (
                    result +
                    _walk_internal(fullname,
                                   (recurse > 1 and [recurse - 1] or [0])[0],
                                   pattern, ignorere, return_folders))

    return result


def filestat(config, filename):
    """
    Returns the filestat on a given file.

    This returns the mtime of the file (same as returned by
    ``time.localtime()``) -- tuple of 9 ints.

    :param config: config
    :param filename: the file name of the file to stat

    :returns: the filestat (tuple of 9 ints) on the given file

    """
    argdict = {
        'config': config,
        'filename': filename,
        'mtime': (0,) * 10
    }

    MT = stat.ST_MTIME

    argdict = run_callback('filestat',
                           argdict,
                           mappingfunc=lambda x, y: y,
                           donefunc=lambda x: x and x["mtime"][MT] != 0,
                           defaultfunc=lambda x: x)

    # Since no plugin handled cb_filestat; we default to asking the
    # filesystem
    if argdict['mtime'][MT] == 0:
        argdict['mtime'] = os.stat(filename)

    timetuple = time.localtime(argdict['mtime'][MT])

    return timetuple


def what_ext(extensions, filepath):
    """
    Takes in a filepath and a list of extensions and tries them all
    until it finds the first extension that works.

    :param extensions: the list of extensions to test
    :param filepath: the complete file path (minus the extension) to
                     test and find the extension for

    :returns: the extension (string) of the file or ``None``.
    """
    for ext in extensions:
        if os.path.isfile(filepath + '.' + ext):
            return ext
    return None


def importname(modulename, name):
    """
    Safely imports modules for runtime importing.

    :param modulename: the package name of the module to import from
    :param name: the name of the module to import

    :returns: the module object or ``None`` if there were problems
              importing.
    """
    logger = logging.getLogger()
    if not modulename:
        m = name
    else:
        m = '%s.%s' % (modulename, name)

    try:
        module = __import__(m)
        for c in m.split('.')[1:]:
            module = getattr(module, c)
        return module

    except ImportError as ie:
        logger.error('Module %s in package %s won\'t import: %s' %
                     (repr(modulename), repr(name), ie))

    except StandardError as e:
        logger.error('Module %s not in in package %s: %s' %
                     (repr(modulename), repr(name), e))

    return None


def run_callback(chain, input,
                 mappingfunc=lambda x, y: x,
                 donefunc=lambda x: 0,
                 defaultfunc=None):
    """
    Executes a callback chain on a given piece of data.  passed in is
    a dict of name/value pairs.  Consult the documentation for the
    specific callback chain you're executing.

    Callback chains should conform to their documented behavior.  This
    function allows us to do transforms on data, handling data, and
    also callbacks.

    The difference in behavior is affected by the mappingfunc passed
    in which converts the output of a given function in the chain to
    the input for the next function.

    If this is confusing, read through the code for this function.

    Returns the transformed input dict.

    :param chain: the name of the callback chain to run

    :param input: dict with name/value pairs that gets passed as the
                  args dict to all callback functions

    :param mappingfunc: the function that maps output arguments to
                        input arguments for the next iteration.  It
                        must take two arguments: the original dict and
                        the return from the previous function.  It
                        defaults to returning the original dict.

    :param donefunc: this function tests whether we're done doing what
                     we're doing.  This function takes as input the
                     output of the most recent iteration.  If this
                     function returns True then we'll drop out of the
                     loop.  For example, if you wanted a callback to
                     stop running when one of the registered functions
                     returned a 1, then you would pass in:
                     ``donefunc=lambda x: x`` .

    :param defaultfunc: if this is set and we finish going through all
                        the functions in the chain and none of them
                        have returned something that satisfies the
                        donefunc, then we'll execute the defaultfunc
                        with the latest version of the input dict.

    :returns: varies
    """
    chain = plugin_utils.get_callback_chain(chain)
    output = None

    for func in chain:
        # we call the function with the input dict it returns an
        # output.
        output = func(input)

        # we fun the output through our donefunc to see if we should
        # stop iterating through the loop.  if the donefunc returns
        # something true, then we're all done; otherwise we continue.
        if donefunc(output):
            break

        # we pass the input we just used and the output we just got
        # into the mappingfunc which will give us the input for the
        # next iteration.  in most cases, this consists of either
        # returning the old input or the old output--depending on
        # whether we're transforming the data through the chain or
        # not.
        input = mappingfunc(input, output)

    # if we have a defaultfunc and we haven't satisfied the donefunc
    # conditions, then we return whatever the defaultfunc returns when
    # given the current version of the input.
    if callable(defaultfunc) and not donefunc(output):
        return defaultfunc(input)

    # we didn't call the defaultfunc--so we return the most recent
    # output.
    return output


def create_entry(datadir, category, filename, mtime, title, metadata, body):
    """
    Creates a new entry in the blog.

    This is primarily used by the testing system, but it could be used
    by scripts and other tools.

    :param datadir: the datadir
    :param category: the category the entry should go in
    :param filename: the name of the blog entry (filename and
                     extension--no directory)
    :param mtime: the mtime (float) for the entry in seconds since the
                  epoch
    :param title: the title for the entry
    :param metadata: dict of key/value metadata pairs
    :param body: the body of the entry

    :raises IOError: if the datadir + category directory exists, but
                     isn't a directory
    """

    # format the metadata lines for the entry
    metadatalines = ['#{0} {1}'.format(key, metadata[key])
                     for key in metadata.keys()]

    if not title.endswith('\n'):
        title = title + '\n'

    entry = title + '\n'.join(metadatalines) + body

    # create the category directories
    d = os.path.join(datadir, category)
    if not os.path.exists(d):
        os.makedirs(d)

    if not os.path.isdir(d):
        raise IOError('{0} exists, but is not a directory.'.format(d))

    # create the filename
    fn = os.path.join(datadir, category, filename)

    # write the entry to disk
    with open(fn, 'w') as fp:
        fp.write(entry)

    # set the mtime on the entry
    os.utime(fn, (mtime, mtime))


def render_url_statically(cfg, url, querystring):
    """Renders a url and saves the rendered output to the
    filesystem.

    :param cfg: config dict
    :param url: url to render
    :param querystring: querystring of the url to render or ""

    """
    compiledir = cfg.get("compiledir", "")

    # If there is no compile_dir, then they're not set up for
    # compiling.
    if not compiledir:
        raise Exception("You must set compiledir in your config file.")

    response = render_url(cfg, url, querystring)
    response.seek(0)

    fn = os.path.normpath(compiledir + os.sep + url)
    if not os.path.isdir(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))

    # Write just the response data to the file skipping the headers.
    with open(fn, 'w') as fp:
        fp.write(response.read())


def copy_dir(src, dst, notifyfun):
    for root, dirs, files in os.walk(src):
        dst_root = os.path.join(dst, root[len(src):].lstrip('/'))
        for name in dirs:
            if not os.path.exists(os.path.join(dst_root, name)):
                os.makedirs(os.path.join(dst_root, name))

        for name in files:
            notifyfun(os.path.join(dst_root, name))
            shutil.copy2(os.path.join(root, name),
                         os.path.join(dst_root, name))


def url_rewrite(html, old_url, new_url):
    out = []

    class URLRewriter(HTMLParser.HTMLParser):
        def __init__(self, old_url, new_url):
            self.old_url_parts = urlsplit(old_url)
            self.new_url_parts = urlsplit(new_url)
            HTMLParser.HTMLParser.__init__(self)

        def rewrite(self, url):
            url_parts = urlsplit(url)

            # Check to see if this is a url to rewrite. If not, skip it.
            if ((url_parts.netloc != self.old_url_parts.netloc
                 or not url_parts.path.startswith(self.old_url_parts.path))):
                return url

            # Rebuild the url using parts from the new_url_parts and
            # the path from the url minus the old_url_path.
            return urlunsplit(
                (self.new_url_parts.scheme,
                 self.new_url_parts.netloc,
                 (self.new_url_parts.path +
                  url_parts.path[len(self.old_url_parts.path):]),
                 url_parts.query,
                 url_parts.fragment))

        def handle_starttag(self, tag, attrs, closed=False):
            # We want to re
            # We want to translate alt and title values, but that's
            # it. So this gets a little goofy looking token-wise.

            s = '<' + tag
            for name, val in attrs:
                s += ' '
                s += name
                s += '="'

                if name in ['src', 'href']:
                    s += self.rewrite(val)
                elif val:
                    s += val
                s += '"'
            if closed:
                s += ' /'
            s += '>'

            if s:
                out.append(s)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs, closed=True)

        def handle_endtag(self, tag):
            out.append('</' + tag + '>')

        def handle_data(self, data):
            out.append(data)

        def handle_charref(self, name):
            out.append('&#' + name + ';')

        def handle_entityref(self, name):
            out.append('&' + name + ';')

    URLRewriter(old_url, new_url).feed(html)
    return ''.join(out)


def render_url(cfg, pathinfo, querystring=""):
    """
    Takes a url and a querystring and renders the page that
    corresponds with that by creating a Request and a Douglas object
    and passing it through.  It then returns the resulting Response.

    :param cfg: the config.py dict
    :param pathinfo: the ``PATH_INFO`` string;
        example: ``/dev/douglas/firstpost.html``
    :param querystring: the querystring (if any); example: debug=yes

    :returns: a douglas ``Response`` object.

    """
    from douglas.app import Douglas

    if querystring:
        request_uri = pathinfo + '?' + querystring
    else:
        request_uri = pathinfo

    parts = urlparse(cfg.get('base_url', ''))

    env = {
        'HTTP_HOST': parts.netloc,
        'HTTP_PORT': parts.port,
        'HTTP_USER_AGENT': 'static renderer',
        'PATH_INFO': pathinfo,
        'QUERY_STRING': querystring,
        'REMOTE_ADDR': '',
        'REQUEST_METHOD': 'GET',
        'REQUEST_URI': request_uri,
        'SCRIPT_NAME': '',
        'wsgi.url_scheme': 'http',
        'wsgi.errors': sys.stderr,
        'wsgi.input': None
    }

    p = Douglas(cfg, env, {'COMPILING': 1})
    p.run(compiling=True)
    return p.get_response()


class URLRouter(object):
    def __init__(self, *routes):
        # A route is a (regex, testfun)
        self.routes = routes

    def match(self, cfg, url):
        for route in self.routes:
            match = re.match(route[0], url)
            if not match:
                continue

            data = dict(
                (key, val) for key, val in match.groupdict().items()
                if val is not None)

            if route[1] is not None:
                data = route[1](cfg, url, data)

            if data:
                return data


LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


def setup_logging(cfg):
    level = cfg.get('log_level', 'error')
    level = LEVELS[level]

    if cfg.get('log_file') is None:
        # If no log file is set up, set to logging.ERROR and stderr.
        logging.basicConfig(level=level, stream=sys.stderr)
    else:
        logging.basicConfig(level=level, filename=cfg['log_file'],
                            filemode='a')
