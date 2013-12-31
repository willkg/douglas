"""
Testing utilities.

Includes up a number of mocks, environment variables, and Douglas
data structures for useful testing plugins.
"""

import StringIO
import cgi
import os
import os.path
import shutil
import tempfile
import time
import unittest
import urllib

from nose.tools import eq_

from douglas import app
from douglas import entries
from douglas.settings import Config
from douglas import tools


def req_():
    return app.Request({}, {}, {})


class UnitTestBase(unittest.TestCase):
    def setUp(self):
        self.blogdir = tempfile.mkdtemp(prefix='douglas_test_blog')
        self.datadir = os.path.join(self.blogdir, 'entries')
        os.makedirs(self.datadir)
        self.themedir = os.path.join(self.blogdir, 'themes')
        os.makedirs(self.themedir)

    def tearDown(self):
        if self.datadir:
            shutil.rmtree(self.datadir, ignore_errors=True)

    def create_file(self, file_path, data):
        fn = os.path.join(self.datadir, file_path)
        dir_ = os.path.dirname(fn)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        with open(fn, 'w') as fp:
            fp.write(data)
        return fn

    def setup_files(self, files):
        os.makedirs(os.path.join(self.datadir, 'entries'))
        for fn in sorted(files):
            d, f = os.path.split(fn)

            if not os.path.exists(d):
                os.makedirs(d)

            if f:
                with open(fn, 'w') as fp:
                    fp.write('test file: {0}\n'.format(fn))

    def build_file_set(self, filelist):
        return [os.path.join(self.datadir, '%s' % fn) for fn in filelist]

    def build_request(self, cfg=None, http=None, data=None, inputstream=""):
        """
        process_path_info uses:
        - req.pyhttp["PATH_INFO"]         - string

        - req.config["default_theme"]     - string
        - req.config["datadir"]           - string
        - req.config["blog_title"]        - string
        - req.config["base_url"]          - string
        - req.config["extensions"]        - dict of string -> func

        if using req.get_form():
        - req.pyhttp["wsgi.input"]        - StringIO instance
        - req.pyhttp["REQUEST_METHOD"]    - GET or POST
        - req.pyhttp["CONTENT_LENGTH"]    - integer
        """
        _config = {
            'default_theme': 'html',
            'datadir': self.datadir,
            'themedir': self.themedir,
            'blog_title': 'My blog',
            'base_url': 'http://www.example.com'
        }
        if cfg:
            _config.update(cfg)

        _config = Config.validate(_config)
        app.initialize(_config)

        _data = {}
        if data:
            _data.update(data)

        _http = {'wsgi.input': StringIO.StringIO(inputstream),
                 'REQUEST_METHOD': len(inputstream) and 'GET' or 'POST',
                 'CONTENT_LENGTH': len(inputstream)}
        if http:
            _http.update(http)

        return app.Request(_config, _http, _data)

    def dictsubset(self, expected, actual):
        for key, val in expected.items():
            eq_(actual[key], val)


class TestTestInfrastructure(UnitTestBase):
    def test_setup_teardown(self):
        """Test the setup/teardown for UnitTestBase"""
        fileset1 = self.build_file_set([
            'file.txt', 'cata/file.txt', 'cata/subcatb/file.txt'])

        self.setup_files(fileset1)
        try:
            for mem in fileset1:
                assert os.path.isfile(mem)

        finally:
            self.tearDown()

        for mem in fileset1:
            assert not os.path.isfile(mem)


TIMESTAMP = time.mktime(time.strptime('Wed Dec 26 11:00:00 2007'))


class FrozenTime(object):
    """Wraps the time module to provide a single, frozen timestamp.

    Allows for dependency injection.

    """
    def __init__(self, timestamp):
        """Sets the time to timestamp, as seconds since the epoch."""
        self.timestamp = timestamp

    def __getattr__(self, attr):
        if attr == 'time':
            return lambda: self.timestamp
        else:
            return getattr(time, attr)


class PluginTest(UnitTestBase):
    """Base class for plugin unit tests. Subclass this to test
    plugins.

    Many common Douglas data structures are populated as attributes
    of this class, including self.environ, self.config, self.data,
    self.request, and self.args.

    By default, self.request is configured as a request for a single
    entry; its name is stored in self.entry_name. This can be
    overridden by modifying the attributes above in your test's
    setUp() method. The entry's timestamp, as seconds since the epoch,
    is stored in self.timestamp. String representations in
    self.timestamp_str and self.timestamp_w3c.

    You can change any of the data structures by modifying them
    directly in your tests or your subclass's setUp() method.

    The datadir is set to a unique temporary directory in /tmp. This
    directory is created fresh for each test, and deleted when the
    test is done.

    NOTE(ryanbarrett): Creating and deleting multiple files and
    directories for each test is inefficient. If this becomes a
    bottleneck, it might need to be reconsidered.
    """

    def setUp(self, plugin_module):
        """Subclasses should call this in their setUp() methods.

        The plugin_module arg is the plugin module being tested. This
        is used to set the plugin_dir config variable.
        """
        UnitTestBase.setUp(self)

        # freeze time
        self.timestamp = TIMESTAMP
        self.frozen_time = self.freeze_douglas_time(self.timestamp)
        self.timestamp_asc = time.ctime(self.timestamp)
        gmtime = time.gmtime(self.timestamp)
        self.timestamp_date = time.strftime('%a %d %b %Y', gmtime)
        self.timestamp_w3c = time.strftime('%Y-%m-%dT%H:%M:%SZ', gmtime)

        plugin_file = os.path.dirname(plugin_module.__file__)
        self.config = Config.validate({
            'datadir': self.datadir,
            'themedir': self.themedir,
            'plugin_dirs': [plugin_file],
            'base_url': 'http://example.com',
        })

        # set up environment vars and http request
        self.environ = {'PATH_INFO': '/', 'REMOTE_ADDR': ''}
        self.form_data = ''
        self.request = app.Request(self.config, self.environ, {})
        self.http = self.request.get_http()

        # set up entries and data dict
        self.data = {
            'entry_list': self.generate_entry_list(self.request, 1),
            'bl_type': 'entry',
        }
        self.request._data = self.data

        # this stores the callbacks that have been injected. it maps
        # callback names to the injected methods to call. any
        # callbacks that haven't been injected are passed through to
        # Douglas's callback chain.
        #
        # use inject_callback() to inject a callback.
        self.injected_callbacks = {}
        orig_run_callback = tools.run_callback

        def intercept_callback(name, args, **kwargs):
            if name in self.injected_callbacks:
                return self.injected_callbacks[name]()
            else:
                return orig_run_callback(name, args, **kwargs)

        tools.run_callback = intercept_callback

    def generate_entry_list(self, req, num=1):
        gmtime = time.gmtime(self.timestamp)
        entry_list = []
        for i in range(num):
            entry_list.append(entries.base.generate_entry(
                req, {'fn': 'test_entry{0}'.format(i)}, {}, gmtime))
        return entry_list

    def freeze_douglas_time(self, timestamp):
        """Injects a frozen time module into Douglas.

        The timestamp argument should be seconds since the epoch. Returns the
        FrozenTime instance.
        """
        assert isinstance(timestamp, (int, float))
        frozen_time = FrozenTime(timestamp)
        app.time = frozen_time
        tools.time = frozen_time
        return frozen_time

    def add_form_data(self, args):
        """Adds the given argument names and values to the request's form data.

        The argument names and values are URL-encoded and escaped before
        populating them in the request. This method also sets the request
        method to POST.
        """
        self.environ['REQUEST_METHOD'] = 'POST'
        self.request.add_http({'REQUEST_METHOD': 'POST'})

        encoded = ['%s=%s' % (arg, urllib.quote(val))
                   for arg, val in args.items()]
        self.form_data += ('&' + '&'.join(encoded))
        input_ = StringIO.StringIO(self.form_data)
        self.request._form = cgi.FieldStorage(fp=input_, environ=self.environ)

    def set_form_data(self, args):
        """Clears the request's form data, then adds the given
        arguments.
        """
        self.form_data = ''
        self.add_form_data(args)

    def inject_callback(self, name, callback):
        """Injects a callback to be run by tools.run_callback().

        The callback is run *instead* of Douglas's standard callback
        chain.
        """
        self.injected_callbacks[name] = callback
