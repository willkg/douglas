# Python imports
import cgi
import locale
import logging
import os
import os.path
import sys
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# Douglas imports
from douglas import __version__
from douglas import crashhandling
from douglas import plugin_utils
from douglas import tools
from douglas.entries.fileentry import FileEntry
from douglas.settings import import_config


def initialize(cfg):
    # import and initialize plugins
    plugin_utils.initialize_plugins(cfg['plugin_dirs'], cfg['load_plugins'])

    # entryparser callback is run here first to allow other
    # plugins register what file extensions can be used
    extensions = tools.run_callback(
        "entryparser",
        {'txt': blosxom_entry_parser},
        mappingfunc=lambda x, y: y,
        defaultfunc=lambda x: x)

    # go through the config.py and override entryparser extensions
    for ext, parser_module in cfg['entryparsers'].items():
        module, callable_name = parser_module.rsplit(':', 1)
        module = tools.importname(None, module)
        extensions[ext] = getattr(module, callable_name)

    # FIXME - this is a lousy place to store this
    cfg['extensions'] = extensions


class Douglas(object):
    """Main class for Douglas functionality.  It handles
    initialization, defines default behavior, and also pushes the
    request through all the steps until the output is rendered and
    we're complete.
    """
    def __init__(self, config, environ, data=None):
        """Sets configuration and environment and creates the Request
        object.

        :param config: dict containing the configuration variables.
        :param environ: dict containing the environment variables.
        :param data: dict containing data variables.
        """
        if data is None:
            data = {}
        data['douglas_name'] = "Douglas"
        data['douglas_version'] = __version__

        self._config = config
        self._request = Request(config, environ, data)

    def initialize(self):
        """The initialize step further initializes the Request by
        setting additional information in the ``data`` dict,
        registering plugins, and entryparsers.
        """
        data = self._request.get_data()
        data['pi_bl'] = ''

    def cleanup(self):
        """This cleans up Douglas after a run.

        This should be called when Douglas has done everything it
        needs to do before exiting.
        """
        # Log some useful stuff for debugging.
        log = logging.getLogger()
        response = self.get_response()
        log.debug('status = %s' % response.status)
        log.debug('headers = %s' % response.headers)

    def get_request(self):
        """Returns the Request object for this Douglas instance.
        """
        return self._request

    def get_response(self):
        """Returns the Response object associated with this Request.
        """
        return self._request.get_response()

    def run(self, compiling=False):
        """This is the main loop for Douglas.  This method will run
        the handle callback to allow registered handlers to handle the
        request.  If nothing handles the request, then we use the
        ``default_blosxom_handler``.

        :param compiling: True if Douglas should execute in compiling
            mode and False otherwise.
        """
        self.initialize()

        # Buffer the input stream in a StringIO instance if dynamic
        # rendering is used.  This is done to have a known/consistent
        # way of accessing incomming data.
        if not compiling:
            self.get_request().buffer_input_stream()

        # Run the start callback
        tools.run_callback("start", {'request': self._request})

        # Allow anyone else to handle the request at this point
        handled = tools.run_callback("handle",
                                     {'request': self._request},
                                     mappingfunc=lambda x, y: x,
                                     donefunc=lambda x: x)

        if not handled == 1:
            blosxom_handler(self._request)

        # Do end callback
        tools.run_callback("end", {'request': self._request})

        # We're done, clean up.  Only call this if we're not in
        # compiling mode.
        if not compiling:
            self.cleanup()

    def run_render_one(self, url, headers):
        """Renders a single page from the blog.

        :param url: the url to render--this has to be relative to the
                    base url for this blog.

        :param headers: True if you want headers to be rendered and
                        False if not.
        """
        self.initialize()

        config = self._request.get_configuration()

        if url.find("?") != -1:
            url = url[:url.find("?")]
            query = url[url.find("?")+1:]
        else:
            query = ""

        url = url.replace(os.sep, "/")
        response = tools.render_url(config, url, query)
        if headers:
            response.send_headers(sys.stdout)
        response.send_body(sys.stdout)

        print response.read()

        # we're done, clean up
        self.cleanup()

    def run_compile(self, incremental=False):
        """Compiles the blog into an HTML site.

        This will go through all possible things in the blog and
        compile the blog to the ``compiledir`` specified in the config
        file.

        This figures out all the possible ``path_info`` settings and
        calls ``self.run()`` a bazillion times saving each file.

        :param incremental: Whether (True) or not (False) to compile
            incrementally. If we're incrementally compiling, then only
            the urls that are likely to have changed get re-compiled.

        """
        self.initialize()

        cfg = self._request.get_configuration()
        compiledir = cfg['compiledir']
        datadir = cfg['datadir']

        if not compiledir:
            print 'Error: You must set compiledir in your config file.'
            return 0

        print 'Compiling to "{0}".'.format(compiledir)
        if incremental:
            print 'Incremental is set.'
        print ''

        themes = cfg['compile_themes']
        index_themes = cfg['compile_index_themes']

        dayindexes = cfg['day_indexes']
        monthindexes = cfg['month_indexes']
        yearindexes = cfg['year_indexes']

        renderme = []
        dates = {}
        categories = {}

        # first we handle entries and categories
        listing = tools.get_entries(cfg, datadir)

        for mem in listing:
            # Skip files that have extensions we don't know what to do
            # with.
            ext = os.path.splitext(mem)[1].lstrip('.')
            if not ext in cfg['extensions'].keys():
                continue

            # Get the mtime of the entry.
            mtime = time.mktime(tools.filestat(self._request, mem))

            # remove the datadir from the front and the bit at the end
            mem = mem[len(datadir):mem.rfind('.')]

            # This is the compiled file filename.
            fn = os.path.normpath(compiledir + mem)

            if incremental:
                # If we're incrementally rendering, we check the mtime
                # for the compiled file for one of the themes. If the entry
                # is more recent than the compiled version, we recompile.
                # Otherwise we skip it.
                try:
                    smtime = os.stat(fn + '.' + themes[0])[8]
                    if smtime < mtime or not incremental:
                        continue

                except (IOError, OSError):
                    pass

            # Figure out category indexes to re-render.
            temp = os.path.dirname(mem).split(os.sep)
            for i in range(len(temp)+1):
                p = os.sep.join(temp[0:i])
                categories[p] = 0

            # Figure out year/month/day indexes to re-render.
            mtime = time.localtime(mtime)
            year = time.strftime('%Y', mtime)
            month = time.strftime('%m', mtime)
            day = time.strftime('%d', mtime)

            if yearindexes:
                dates[year] = 1

            if monthindexes:
                dates[year + '/' + month] = 1

            if dayindexes:
                dates[year + '/' + month + '/' + day] = 1

            # Toss each theme for this entry in the render queue.
            for f in themes:
                renderme.append((mem + '.' + f, ''))

        print '- Found {0} entry(es) ...'.format(len(renderme))

        if categories:
            categories = sorted(categories.keys())

            # if they have stuff in their root category, it'll add a "/"
            # to the category list and we want to remove that because it's
            # a duplicate of "".
            if '/' in categories:
                categories.remove('/')

            print '- Found {0} category index(es) ...'.format(len(categories))

            for mem in categories:
                mem = os.path.normpath(mem + '/index.')
                for f in index_themes:
                    renderme.append((mem + f, ''))

        if dates:
            dates = ['/' + d for d in sorted(dates.keys())]

            print '- Found {0} date index(es) ...'.format(len(dates))

            for mem in dates:
                mem = os.path.normpath(mem + '/index.')
                for f in index_themes:
                    renderme.append((mem + f, ''))

        additional_stuff = cfg['compile_urls']
        if additional_stuff:
            print '- Found {0} arbitrary url(s) ...'.format(
                len(additional_stuff))

            for mem in additional_stuff:
                if mem.find('?') != -1:
                    url = mem[:mem.find('?')]
                    query = mem[mem.find('?')+1:]
                else:
                    url = mem
                    query = ''

                renderme.append((url, query))

        # Pass the complete render list to all the plugins via
        # cb_compile_filelist and they can add to the filelist any
        # (url, query) tuples they want rendered.
        total = len(renderme)
        tools.run_callback('compile_filelist',
                           {'request': self._request,
                            'filelist': renderme,
                            'themes': themes,
                            'incremental': incremental})

        renderme = sorted(set(renderme))
        print '- Found {0} url(s) specified by plugins ...'.format(
            len(renderme) - total)

        print ''
        print 'Compiling {0} url(s) total.'.format(len(renderme))
        print ''

        print 'Rendering files ...'
        for url, q in renderme:
            url = url.replace(os.sep, '/')
            print '   Rendering {0} ...'.format(url)
            tools.render_url_statically(dict(cfg), url, q)

        # We're done, clean up
        self.cleanup()

    def run_collectstatic(self):
        """Collects static files and copies them to compiledir"""

        # FIXME: rewrite using tools.get_static_files(cfg)

        cfg = self._request.get_configuration()

        self.initialize()

        # Copy over static files
        print 'Copying over static files ...'
        dst = os.path.join(cfg['compiledir'], 'static')
        if not os.path.exists(dst):
            os.makedirs(dst)

        def notifyfun(filename):
            print '   Copying {0}'.format(filename)

        # Copy over static_files_dirs files first
        static_files_dirs = cfg['static_files_dirs']
        static_files_dirs.append(os.path.join(cfg['datadir'], '..', 'static'))
        for mem in static_files_dirs:
            tools.copy_dir(mem, dst, notifyfun=notifyfun)

        # Copy over themes static dirs
        for mem in os.listdir(cfg['themedir']):
            path = os.path.join(cfg['themedir'], mem, 'static')
            if os.path.exists(path):
                tools.copy_dir(path, dst, notifyfun=notifyfun)

        # We're done, clean up
        self.cleanup()


class DouglasWSGIApp(object):
    def __init__(self, environ=None, start_response=None, configini=None):
        """
        Make WSGI app for Douglas.

        :param environ: FIXME

        :param start_response: FIXME

        :param configini: Dict encapsulating information from a
                          ``config.ini`` file or any other property
                          file that will override the ``config.py``
                          file.
        """
        self.environ = environ
        self.start_response = start_response

        self.config = import_config()
        if configini is not None:
            self.config.update(tools.convert_configini_values(configini))

        tools.setup_logging(self.config)
        initialize(self.config)

    def run_douglas(self, env, start_response):
        """Executes a single run of Douglas wrapped in the crash handler."""
        response = None
        try:
            # ensure that PATH_INFO exists. a few plugins break if this is
            # missing.
            if 'PATH_INFO' not in env:
                env['PATH_INFO'] = ''

            p = Douglas(dict(self.config), env)
            p.run()
            response = p.get_response()

        except Exception:
            ch = crashhandling.CrashHandler(True, env)
            response = ch.handle_by_response(*sys.exc_info())

        start_response(response.status, list(response.headers.items()))
        response.seek(0)
        return response.read()

    def __call__(self, env, start_response):
        return [self.run_douglas(env, start_response)]

    def __iter__(self):
        yield self.run_douglas(self.environ, self.start_response)


def douglas_app_factory(global_config, **local_config):
    """App factory for paste.

    :returns: WSGI application

    """
    conf = global_config.copy()
    conf.update(local_config)
    conf.update(dict(local_config=local_config, global_config=global_config))

    if "configpydir" in conf:
        sys.path.insert(0, conf["configpydir"])

    return DouglasWSGIApp(configini=conf)


class EnvDict(dict):
    """Wrapper arround a dict to provide a backwards compatible way to
    get the ``form`` with syntax as::

        request.get_http()['form']

    instead of::

        request.get_form()

    """
    def __init__(self, request, env):
        """Wraps an environment (which is a dict) and a request.

        :param request: the Request object for this request.
        :param env: the environment dict for this request.
        """
        dict.__init__(self)
        self._request = request
        self.update(env)

    def __getitem__(self, key):
        """If the key argument is ``form``, we return
        ``_request.get_form()``.  Otherwise this returns the item for
        that key in the wrapped dict.
        """
        if key == 'form':
            return self._request.get_form()

        return dict.__getitem__(self, key)


class Request(object):
    """
    This class holds the Douglas request.  It holds configuration
    information, HTTP/CGI information, and data that we calculate and
    transform over the course of execution.

    There should be only one instance of this class floating around
    and it should get created by ``douglas.cgi`` and passed into the
    Douglas instance which will do further manipulation on the
    Request instance.
    """
    def __init__(self, config, environ, data):
        """Sets configuration and environment.

        Creates the Response object which handles all output related
        functionality.

        :param config: dict containing configuration variables.
        :param environ: dict containing environment variables.
        :param data: dict containing data variables.
        """
        # this holds configuration data that the user changes in
        # config.py
        self._configuration = config

        # this holds HTTP/CGI oriented data specific to the request
        # and the environment in which the request was created
        self._http = EnvDict(self, environ)

        # this holds run-time data which gets created and transformed
        # by douglas during execution
        if data is None:
            self._data = dict()
        else:
            self._data = data

        # this holds the input stream.  initialized for dynamic
        # rendering in Douglas.run.  for compiling there is no input
        # stream.
        self._in = StringIO()

        # copy methods to the Request object.
        self.read = self._in.read
        self.readline = self._in.readline
        self.readlines = self._in.readlines
        self.seek = self._in.seek
        self.tell = self._in.tell

        # this holds the FieldStorage instance.
        # initialized when request.get_form is called the first time
        self._form = None

        self._response = None

        # create and set the Response
        self.set_response(Response(self))

    def __iter__(self):
        """
        Can't copy the __iter__ method over from the StringIO instance
        cause iter looks for the method in the class instead of the
        instance.

        See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252151
        """
        return self._in

    def buffer_input_stream(self):
        """
        Buffer the input stream in a StringIO instance.  This is done
        to have a known/consistent way of accessing incomming data.
        For example the input stream passed by mod_python does not
        offer the same functionallity as ``sys.stdin``.
        """
        # TODO: tests on memory consumption when uploading huge files
        pyhttp = self.get_http()
        winput = pyhttp['wsgi.input']
        method = pyhttp['REQUEST_METHOD']

        # there's no data on stdin for a GET request.  douglas
        # will block indefinitely on the read for a GET request with
        # thttpd.
        if method != 'GET':
            try:
                length = int(pyhttp.get('CONTENT_LENGTH', 0))
            except ValueError:
                length = 0

            if length > 0:
                self._in.write(winput.read(length))
                # rewind to start
                self._in.seek(0)

    def set_response(self, response):
        """Sets the Response object."""
        self._response = response
        # for backwards compatibility
        self.get_configuration()['stdoutput'] = response

    def get_response(self):
        """Returns the Response for this request."""
        return self._response

    def _getform(self):
        form = cgi.FieldStorage(fp=self._in,
                                environ=self._http,
                                keep_blank_values=0)
        # rewind the input buffer
        self._in.seek(0)
        return form

    def get_form(self):
        """Returns the form data submitted by the client.  The
        ``form`` instance is created only when requested to prevent
        overhead and unnecessary consumption of the input stream.

        :returns: a ``cgi.FieldStorage`` instance.
        """
        if self._form is None:
            self._form = self._getform()
        return self._form

    def get_theme(self):
        """Returns the user-requested theme."""
        form = self.get_form()
        if 'theme' in form:
            return form['theme'].value
        pathinfo = self.get_http().get('PATH_INFO', '')
        path, ext = os.path.splitext(pathinfo)
        if ext:
            return ext[1:]
        return self.get_configuration()['default_theme']

    def get_configuration(self):
        """Returns the *actual* configuration dict.  The configuration
        dict holds values that the user sets in their ``config.py``
        file.

        Modifying the contents of the dict will affect all downstream
        processing.
        """
        return self._configuration

    def get_http(self):
        """Returns the *actual* http dict.  Holds HTTP/CGI data
        derived from the environment of execution.

        Modifying the contents of the dict will affect all downstream
        processing.
        """
        return self._http

    def get_data(self):
        """Returns the *actual* data dict.  Holds run-time data which
        is created and transformed by douglas during execution.

        Modifying the contents of the dict will affect all downstream
        processing.
        """
        return self._data

    def add_http(self, d):
        """Takes in a dict and adds/overrides values in the existing
        http dict with the new values.
        """
        self._http.update(d)

    def add_data(self, d):
        """Takes in a dict and adds/overrides values in the existing
        data dict with the new values.
        """
        self._data.update(d)

    def add_configuration(self, newdict):
        """Takes in a dict and adds/overrides values in the existing
        configuration dict with the new values.
        """
        self._configuration.update(newdict)

    def __getattr__(self, name):
        if name in ["config", "configuration", "conf"]:
            return self._configuration

        if name == "data":
            return self._data

        if name == "http":
            return self._http

        raise AttributeError(name)

    def __repr__(self):
        return "Request"


class Response(object):
    """Response class to handle all output related tasks in one place.

    This class is basically a wrapper arround a ``StringIO`` instance.
    It also provides methods for managing http headers.
    """
    def __init__(self, request):
        """Sets the ``Request`` object that leaded to this response.
        Creates a ``StringIO`` that is used as a output buffer.
        """
        self._request = request
        self._out = StringIO()
        self._headers_sent = False
        self.headers = {}
        self.status = "200 OK"

        self.close = self._out.close
        self.flush = self._out.flush
        self.read = self._out.read
        self.readline = self._out.readline
        self.readlines = self._out.readlines
        self.seek = self._out.seek
        self.tell = self._out.tell
        self.write = self._out.write
        self.writelines = self._out.writelines

    def __iter__(self):
        """Can't copy the ``__iter__`` method over from the
        ``StringIO`` instance because iter looks for the method in the
        class instead of the instance.

        See
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252151
        """
        return self._out

    def set_status(self, status):
        """Sets the status code for this response.  The status should
        be a valid HTTP response status.

        Examples:

        >>> resp.set_status("200 OK")
        >>> resp.set_status("404 Not Found")

        :param status: the status string.

        """
        self.status = status

    def get_status(self):
        """Returns the status code and message of this response.
        """
        return self.status

    def add_header(self, key, value):
        """Populates the HTTP header with lines of text.  Sets the
        status code on this response object if the given argument list
        containes a 'Status' header.

        Example:

        >>> resp.add_header("Content-type", "text/plain")
        >>> resp.add_header("Content-Length", "10500")

        :raises ValueError: This happens when the parameters are
                            not correct.

        """
        key = key.strip()
        if key.find(' ') != -1 or key.find(':') != -1:
            raise ValueError('There should be no spaces in header keys')
        value = value.strip()
        if key.lower() == "status":
            self.set_status(str(value))
        else:
            self.headers.update({key: str(value)})

    def get_headers(self):
        """Returns the headers.
        """
        return self.headers

    def send_headers(self, out):
        """Send HTTP Headers to the given output stream.

        .. Note::

            This prints the headers and then the ``\\n\\n`` that
            separates headers from the body.

        :param out: The file-like object to print headers to.
        """
        out.write("Status: %s\n" % self.status)
        out.write('\n'.join(['%s: %s' % (hkey, self.headers[hkey])
                             for hkey in self.headers.keys()]))
        out.write('\n\n')
        self._headers_sent = True

    def send_body(self, out):
        """Send the response body to the given output stream.

        :param out: the file-like object to print the body to.
        """
        self.seek(0)
        try:
            out.write(self.read())
        except IOError:
            # this is usually a Broken Pipe because the client dropped the
            # connection.  so we skip it.
            pass


def blosxom_handler(request):
    """This is the default blosxom handler.

    It calls the renderer callback to get a renderer.  If there is no
    renderer, it uses the blosxom renderer.

    It calls the pathinfo callback to process the path_info http
    variable.

    It calls the filelist callback to build a list of entries to
    display.

    It calls the prepare callback to do any additional preparation
    before rendering the entries.

    Then it tells the renderer to render the entries.

    :param request: the request object.
    """
    config = request.get_configuration()
    data = request.get_data()

    # go through the renderer callback to see if anyone else wants to
    # render.  this renderer gets stored in the data dict for
    # downstream processing.
    rend = tools.run_callback('renderer',
                              {'request': request},
                              donefunc=lambda x: x is not None,
                              defaultfunc=lambda x: None)

    if not rend:
        # get the renderer we want to use
        rend = config['renderer']

        # import the renderer
        rend = tools.importname('douglas.renderers', rend)

        # get the renderer object
        rend = rend.Renderer(request, config.get('stdoutput', sys.stdout))

    data['renderer'] = rend

    # generate the timezone variable
    data["timezone"] = time.tzname[time.localtime()[8]]

    # process the path info to determine what kind of blog entry(ies)
    # this is
    tools.run_callback('pathinfo',
                       {'request': request},
                       donefunc=lambda x: x is not None,
                       defaultfunc=blosxom_process_path_info)

    # call the filelist callback to generate a list of entries
    data['entry_list'] = tools.run_callback(
        'filelist',
        {'request': request},
        donefunc=lambda x: x is not None,
        defaultfunc=blosxom_file_list_handler)

    # figure out the blog-level mtime which is the mtime of the head
    # of the entry_list
    entry_list = data['entry_list']
    if isinstance(entry_list, list) and len(entry_list) > 0:
        mtime = entry_list[0].get('mtime', time.time())
    else:
        mtime = time.time()
    mtime_tuple = time.localtime(mtime)
    mtime_gmtuple = time.gmtime(mtime)

    data['latest_date'] = time.strftime('%a, %d %b %Y', mtime_tuple)

    # Make sure we get proper 'English' dates when using standards
    loc = locale.getlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'C')

    data['latest_w3cdate'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                           mtime_gmtuple)
    data['latest_rfc822date'] = time.strftime('%a, %d %b %Y %H:%M GMT',
                                              mtime_gmtuple)

    # set the locale back
    locale.setlocale(locale.LC_ALL, loc)

    # we pass the request with the entry_list through the prepare
    # callback giving everyone a chance to transform the data.  the
    # request is modified in place.
    tools.run_callback('prepare', {'request': request})

    # now we pass the entry_list through the renderer
    entry_list = data['entry_list']
    renderer = data['renderer']

    if renderer and not renderer.rendered:
        if entry_list:
            renderer.set_content(entry_list)
        else:
            # FIXME - We should have a 404 template. Instead, we're
            # going to fake the entry and use the entry template.
            data['bl_type'] = 'entry'
            renderer.add_header('Status', '404 Not Found')
            renderer.set_content(
                {'title': 'The page you are looking for is not available',
                 'body': 'Somehow I cannot find the page you want. '
                 'Go Back to <a href="{0}">{1}</a>?'.format(
                     config['base_url'], config['blog_title'])})
        renderer.render()

    elif not renderer:
        output = config.get('stdoutput', sys.stdout)
        output.write(
            'Content-Type: text/plain\n\n'
            'There is something wrong with your setup.\n'
            'Check your config files and verify that your '
            'configuration is correct.\n')


def blosxom_entry_parser(filename, request):
    """Parses a ``.txt`` entry file.

    The first line becomes the title of the entry.  Lines after the
    first line that start with ``#`` are metadata lines.  After the
    metadata lines, the remaining lines are the body of the entry.

    :param filename: a filename to extract data and metadata from
    :param request: a standard request object

    :returns: dict containing parsed data and meta data with the
              particular file (and plugin)

    """
    cfg = request.get_configuration()
    return dict(tools.parse_entry_file(filename, cfg['blog_encoding']))


def blosxom_file_list_handler(args):
    """This is the default handler for getting entries.  It takes the
    request object in and figures out which entries based on the
    default behavior that we want to show and generates a list of
    EntryBase subclass objects which it returns.

    :param args: dict containing the incoming Request object

    :returns: the content we want to render
    """
    request = args["request"]

    data = request.get_data()
    config = request.get_configuration()

    if data['bl_type'] == 'entry_list':
        filelist = tools.get_entries(
            config, data['root_datadir'], int(config['depth']))
    elif data['bl_type'] == 'entry':
        filelist = [data['root_datadir']]
    else:
        filelist = []

    entrylist = [FileEntry(request, e, data["root_datadir"]) for e in filelist]

    # if we're looking at a set of archives, remove all the entries
    # that aren't in the archive
    if data.get("pi_yr"):
        datestr = "%s%s%s" % (data["pi_yr"],
                              data.get("pi_mo", ""),
                              data.get("pi_da", ""))
        entrylist = [
            x for x in entrylist
            if (time.strftime("%Y%m%d%H%M%S", x["timetuple"])
                .startswith(datestr))]

    args = {"request": request, "entry_list": entrylist}
    entrylist = tools.run_callback("sortlist",
                                   args,
                                   donefunc=lambda x: x is not None,
                                   defaultfunc=blosxom_sort_list_handler)

    args = {"request": request, "entry_list": entrylist}
    entrylist = tools.run_callback("truncatelist",
                                   args,
                                   donefunc=lambda x: x is not None,
                                   defaultfunc=blosxom_truncate_list_handler)

    return entrylist


def blosxom_sort_list_handler(args):
    """Sorts the list based on ``_mtime`` attribute such that
    most recently written entries are at the beginning of the list
    and oldest entries are at the end.

    :param args: args dict with ``request`` object and ``entry_list``
                 list of entries

    :returns: the sorted ``entry_list``
    """
    entrylist = args["entry_list"]
    entrylist.sort(key=lambda entry: entry._mtime, reverse=True)
    return entrylist


def blosxom_truncate_list_handler(args):
    """If ``config["num_entries"]`` is not 0 and ``data["truncate"]``
    is not 0, then this truncates ``args["entry_list"]`` by
    ``config["num_entries"]``.

    :param args: args dict with ``request`` object and ``entry_list``
                 list of entries

    :returns: the truncated ``entry_list``.
    """
    request = args['request']
    data = request.get_data()
    config = request.get_configuration()

    num_entries = config['num_entries']
    if data.get('truncate', False) and num_entries:
        entrylist = args['entry_list'][:num_entries]
    return entrylist


def route_directory(cfg, url, data):
    path = os.path.join(cfg['datadir'], data.get('path', '').lstrip('/'))
    if os.path.isdir(path):
        data.update({
            'root_datadir': path,
            'bl_type': 'entry_list'
        })
        return data


def route_file(cfg, url, data):
    path = os.path.join(cfg['datadir'], data['path'].lstrip('/'))
    ext = tools.what_ext(cfg['extensions'].keys(), path)
    if ext:
        data.update({
            'root_datadir': path + '.' + ext,
            'bl_type': 'entry'
        })
        return data


def route_date(cfg, url, data):
    if not cfg['day_indexes'] and data.get('pi_da'):
        return

    if not cfg['month_indexes'] and data.get('pi_mo'):
        return

    if not cfg['year_indexes'] and data['pi_yr']:
        return

    data.update({
        'pi_bl': '',
        'bl_type': 'entry_list',
        'root_datadir': os.path.join(cfg['datadir'], url.lstrip('/'))
    })
    return data


ROUTER = tools.URLRouter(
    (r'^$', route_directory),
    (r'^/(?P<path>.*)$', route_directory),
    (r'^/(?P<path>.*?)index$', route_directory),
    (r'^/(?P<path>.*?)index\.(?P<theme>[^./]+)$', route_directory),

    (r'^/(?P<path>.+)$', route_file),
    (r'^/(?P<path>.+)\.(?P<theme>[^./]+)$', route_file),

    (r'^/(?P<pi_yr>\d{4})/?$', route_date),
    (r'^/(?P<pi_yr>\d{4})/index$', route_date),
    (r'^/(?P<pi_yr>\d{4})/index\.(?P<theme>[^./]+)$', route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/?$', route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/index$', route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/index\.(?P<theme>[^./]+)$',
     route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/(?P<pi_da>\d{2})/?$',
     route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/(?P<pi_da>\d{2})/index$',
     route_date),
    (r'^/(?P<pi_yr>\d{4})/(?P<pi_mo>\d{2})/(?P<pi_da>\d{2})/index\.'
     r'(?P<theme>[^./]+)$',
     route_date),
)


def blosxom_process_path_info(args):
    """Process HTTP ``PATH_INFO`` for URI according to path
    specifications, fill in data dict accordingly.

    The paths specification looks like this:

    - ``/foo.html`` and ``/cat/foo.html`` - file foo.* in / and /cat
    - ``/cat`` - category
    - ``/2002`` - category (if that's a directory)
    - ``/2002`` - year index
    - ``/2002/02`` - year/month index
    - ``/2002/02/04`` - year/month/day index

    :param args: dict containing the incoming Request object

    """
    request = args['request']
    cfg = request.get_configuration()
    data = request.get_data()
    pyhttp = request.get_http()

    # Populate with default values
    new_data = {
        'path_info': pyhttp.get('PATH_INFO', ''),
        'pi_yr': '',
        'pi_mo': '',
        'pi_da': '',
        'pi_bl': pyhttp.get('PATH_INFO', ''),
        'bl_type': '',
        'theme': request.get_theme(),
        'root_datadir': cfg['datadir']
    }

    routed_data = ROUTER.match(cfg, new_data['path_info'])

    if not routed_data:
        # If we have no idea what this is, then treat it like a file.
        routed_data = {
            'bl_type': '',
            'root_datadir': os.path.join(cfg['datadir'].rstrip(),
                                         pyhttp.get('PATH_INFO', '').lstrip())
        }

    new_data.update(routed_data)

    # Construct final URL
    new_data['url'] = '/'.join([
        cfg['base_url'].rstrip('/\\'), new_data['pi_bl'].lstrip('/\\')])

    # Figure out whether to truncate the entry list
    truncate = False
    if new_data.get('pi_yr'):
        truncate = cfg['truncate_date']
    elif new_data.get('bl_type') == 'entry_list':
        if new_data['path_info'] in ([''], ['index']):
            truncate = cfg['truncate_frontpage']
        else:
            truncate = cfg['truncate_category']
    new_data['truncate'] = truncate

    # Update the data dict in-place
    data.update(new_data)
    return data


def run_cgi(cfg):
    """Executes Douglas as a CGI script."""
    env = {}

    # names taken from wsgi instead of inventing something new
    env['wsgi.input'] = sys.stdin
    env['wsgi.errors'] = sys.stderr

    # figure out what the protocol is for the wsgi.url_scheme
    # property.  we look at the base_url first and if there's nothing
    # set there, we look at environ.
    if 'base_url' in cfg:
        env['wsgi.url_scheme'] = cfg['base_url'][:cfg['base_url'].find("://")]

    else:
        if os.environ.get("HTTPS", "off") in ("on", "1"):
            env["wsgi.url_scheme"] = "https"

        else:
            env['wsgi.url_scheme'] = "http"

    # Run as a WSGI-CGI thing
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(DouglasWSGIApp())
