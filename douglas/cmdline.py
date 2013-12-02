"""
This module holds commandline related stuff.  Installation
verification, blog creation, commandline argument parsing, ...
"""

from SimpleHTTPServer import SimpleHTTPRequestHandler
from functools import wraps
from optparse import OptionParser
from urlparse import urlparse
import SocketServer
import datetime
import os
import os.path
import random
import sys
import time

from douglas import __version__
from douglas import plugin_utils
from douglas.app import Douglas, initialize
from douglas.tools import abort, run_callback, pwrap, pwrap_error, setup_logging


USAGE = "%prog [options] [command] [command-options]"
VERSION = "%prog " + __version__


def import_config(quiet=True):
    if not quiet:
        pwrap("Trying to import the config module....")

    try:
        from config import py as cfg
        return cfg

    except StandardError:
        if not quiet:
            h, t = os.path.split(sys.argv[0])
            scriptname = t or h

            pwrap_error(
                'Error: Cannot find your config.py file.  Please execute '
                '{prog} in the directory with the config.py file in it or '
                'use the --config flag.'
                '\n\n'
                'See "{prog} --help" for more details.'.format(
                    prog=scriptname))
        return {}


def with_config(fun):
    @wraps(fun)
    def _wrapped(*args, **kwargs):
        cfg = import_config(quiet=False)
        return fun(cfg, *args, **kwargs)
    return _wrapped


def build_douglas(cfg):
    """Imports config.py and builds an empty douglas object.
    """
    if not cfg:
        return None

    initialize(cfg)
    setup_logging(cfg)
    return Douglas(cfg, {})


def build_parser(usage):
    parser = OptionParser(usage=usage, version=VERSION)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="If the quiet flag is specified, then douglas "
                      "will run quietly.")
    parser.add_option("--config",
                      help="This specifies the directory that the config.py "
                      "for the blog you want to work with is in.  If the "
                      "config.py file is in the current directory, then "
                      "you don't need to specify this.  All commands except "
                      "the 'create' command need a config.py file.")

    return parser


def generate_handler(cfg, host_port):
    """Creates a closure so our DouglasHTTPRequestHandler has what it needs"""
    base_url = cfg.get('base_url', '/')
    base_path = urlparse(base_url).path.lstrip('/')
    staticdir = cfg['static_dir']
    default_theme = cfg.get('default_theme', 'html')
    serving_base_url = 'http://{0}/{1}'.format(host_port, base_path)

    class DouglasHTTPRequestHandler(SimpleHTTPRequestHandler):
        """Handler that serves compiled_site locally at the right path"""
        def translate_path(self, path):
            """Translate a url path to the local file."""
            newpath = urlparse(path).path
            newpath = newpath.lstrip('/')

            if not newpath.startswith(base_path):
                newpath = base_path
            else:
                newpath = newpath[len(base_path):]

            newpath = newpath.lstrip('/')
            newpath = os.path.join(staticdir, newpath)

            # If the path doesn't exist, try the path with the
            # default_theme tacked on.
            if not os.path.exists(newpath):
                if os.path.exists(newpath + '.' + default_theme):
                    newpath = newpath + '.' + default_theme

            # Do some fancy footwork so we're likely to get a correct
            # content-type.
            if not os.path.isfile(newpath):
                newpath = newpath + 'index.html'

            return newpath

        def do_GET(self):
            if self.path == '/' and base_path:
                # Redirect to the base_path.
                print 'Redirecting to /{0}'.format(base_path)
                self.send_response(302)
                self.send_header("Location", '/' + base_path)
                self.end_headers()
                return

            self._type = self.guess_type(self.translate_path(self.path))

            SimpleHTTPRequestHandler.do_GET(self)

        def copyfile(self, source, outputfile):
            """Copies data over and replaces base_url for html files"""
            if self._type == 'text/html':
                data = source.read()
                data = data.replace(base_url, serving_base_url)
                outputfile.write(data)
            else:
                SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

    return DouglasHTTPRequestHandler


@with_config
def cmd_serve(cfg, command, argv):
    """Serves the compiled_site."""
    parser = build_parser("%prog serve [options]")
    parser.add_option("--host",
                      dest="host_port",
                      help="host:port to serve at",
                      default='127.0.0.1:8000',
                      metavar="HOST")
    (options, args) = parser.parse_args(argv)

    # FIXME - redo value validation here
    host_port = options.host_port
    if ':' not in host_port:
        host_port = host_port + ':8000'

    host, port = host_port.split(':')
    port = int(port)

    handler = generate_handler(cfg, host_port)

    httpd = SocketServer.TCPServer((host, port), handler)
    print 'Serving at http://{0}:{1}'.format(host, port)
    httpd.serve_forever()


@with_config
def cmd_generate(cfg, command, argv):
    """Generates random entries to help with Douglas development."""
    parser = build_parser("%prog generate [options] <num_entries>")
    (options, args) = parser.parse_args(argv)

    if args:
        try:
            num_entries = int(args[0])
            assert num_entries > 0
        except ValueError:
            pwrap_error("ERROR: num_entries must be a positive integer.")
            return 0
    else:
        num_entries = 5

    verbose = options.verbose

    datadir = cfg.get('datadir')
    if not datadir:
        return abort('Error: No datadir.')

    sm_para = "<p>Lorem ipsum dolor sit amet.</p>"
    med_para = """<p>
  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus
  in mi lacus, sed interdum nisi. Vestibulum commodo urna et libero
  vestibulum gravida. Vivamus hendrerit justo quis lorem auctor
  consectetur. Aenean ornare, tortor in sollicitudin imperdiet, neque
  diam pellentesque risus, vitae.
</p>"""
    lg_para = """<p>
  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
  dictum tortor orci. Lorem ipsum dolor sit amet, consectetur
  adipiscing elit. Etiam quis lectus vel odio convallis tincidunt sed
  et magna. Suspendisse at dolor suscipit eros ullamcorper iaculis. In
  aliquet ornare libero eget rhoncus. Sed ac ipsum eget eros fringilla
  aliquet ut eget velit. Curabitur dui nibh, eleifend non suscipit at,
  laoreet ac purus. Morbi id sem diam. Cras sit amet ante lacus, nec
  euismod urna. Curabitur iaculis, lorem at fringilla malesuada, nunc
  ligula eleifend nisi, at bibendum libero est quis
  tellus. Pellentesque habitant morbi tristique senectus et netus et
  malesuada.
</p>"""
    paras = [sm_para, med_para, lg_para]

    if verbose:
        print 'Creating {0} entries'.format(num_entries)

    now = time.time()

    for i in range(num_entries):
        fn = os.path.join(datadir, 'post_{0}.txt'.format(i+1))

        if verbose:
            print 'Creating "{0}"...'.format(fn)

        title = 'post number {0}\n'.format(i+1)
        body = [random.choice(paras) for j in range(random.randrange(1, 6))]

        with open(fn, 'w') as fp:
            fp.write(title)
            fp.write('\n'.join(body))

        mtime = now - ((num_entries - i) * 3600)
        os.utime(fn, (mtime, mtime))

    if verbose:
        print 'Done!'
    return 0


@with_config
def cmd_test(cfg, command, argv):
    """Tests installation and configuration for a blog."""
    # This:
    # 1. verifies config.py file properties
    # 2. initializes all the plugins they have installed
    # 3. runs ``cb_verify_installation``--plugins can print out whether
    #    they are installed correctly (i.e. have valid config property
    #    settings and can read/write to data files)
    #
    # The goal is to be as useful and informative to the user as we can
    # be without being overly verbose and confusing.
    #
    # This is designed to make it easier for a user to verify their
    # douglas installation is working and also to install new plugins
    # and verify that their configuration is correct.

    parser = build_parser("%prog test [options]")
    parser.parse_args(argv)

    pwrap("System Information")
    pwrap("==================")
    pwrap("")

    pwrap("- douglas:      %s" % __version__)
    pwrap("- sys.version:  %s" % sys.version.replace("\n", " "))
    pwrap("- os.name:      %s" % os.name)
    codebase = os.path.dirname(os.path.dirname(__file__))
    pwrap("- codebase:     %s" % cfg.get("codebase", codebase))
    pwrap("")

    pwrap("Checking config.py file")
    pwrap("=======================")
    pwrap("- properties set: %s" % len(cfg))

    cfg_keys = cfg.keys()

    if "datadir" not in cfg_keys:
        pwrap_error("- ERROR: 'datadir' must be set.  Refer to installation "
                    "documentation.")

    elif not os.path.isdir(cfg["datadir"]):
        pwrap_error("- ERROR: datadir '%s' does not exist."
                    "  You need to create your datadir and give it "
                    " appropriate permissions." % cfg["datadir"])
    else:
        pwrap("- datadir '%s' exists." % cfg["datadir"])

    if "themedir" not in cfg_keys:
        pwrap("- WARNING: You should consider setting themedir and putting "
              "your themedir templates there.  See the documentation for "
              "more details.")
    elif not os.path.isdir(cfg["themedir"]):
        pwrap_error("- ERROR: themedir '%s' does not exist."
                    "  You need to create your themedir and give it "
                    " appropriate permissions." % cfg["themedir"])
    else:
        pwrap("- themedir '%s' exists." % cfg["themedir"])

    if (("blog_encoding" in cfg_keys
         and cfg["blog_encoding"].lower() != "utf-8")):
        pwrap_error("- WARNING: 'blog_encoding' is set to something other "
                    "than 'utf-8'.  This isn't a good idea unless you're "
                    "absolutely certain it's going to work for your blog.")
    pwrap("")

    pwrap("Checking plugin configuration")
    pwrap("=============================")

    import traceback

    no_verification_support = []

    if len(plugin_utils.plugins) + len(plugin_utils.bad_plugins) == 0:
        pwrap(" - There are no plugins installed.")

    else:
        if len(plugin_utils.bad_plugins) > 0:
            pwrap("- Some plugins failed to load.")
            pwrap("")
            pwrap("----")
            for mem in plugin_utils.bad_plugins:
                pwrap("plugin:  %s" % mem[0])
                print "%s" % mem[1]
                pwrap("----")
            pwrap_error("FAIL")
            return(1)

        if len(plugin_utils.plugins) > 0:
            pwrap("- This goes through your plugins and asks each of them "
                  "to verify configuration and installation.")
            pwrap("")
            pwrap("----")
            for mem in plugin_utils.plugins:
                if hasattr(mem, "verify_installation"):
                    pwrap("plugin:  %s" % mem.__name__)
                    print "file:    %s" % mem.__file__
                    print "version: %s" % (str(getattr(mem, "__version__")))

                    try:
                        if mem.verify_installation(cfg) == 1:
                            pwrap("PASS")
                        else:
                            pwrap_error("FAIL")
                    except StandardError:
                        pwrap_error("FAIL: Exception thrown:")
                        traceback.print_exc(file=sys.stdout)

                    pwrap("----")
                else:
                    mn = mem.__name__
                    mf = mem.__file__
                    no_verification_support.append("'%s' (%s)" % (mn, mf))

            if len(no_verification_support) > 0:
                pwrap("")
                pwrap("The following plugins do not support installation "
                      "verification:")
                no_verification_support.sort()
                for mem in no_verification_support:
                    print "- %s" % mem

    pwrap("")
    pwrap("Verification complete.  Correct any errors and warnings above.")


def cmd_create(command, argv):
    """Creates directory structure for new blog."""
    parser = build_parser("%prog create [options] <dir>")
    (options, args) = parser.parse_args(argv)

    if args:
        d = args[0]
    else:
        d = "."

    if d == ".":
        d = "." + os.sep + "blog"

    d = os.path.abspath(d)

    verbose = options.verbose

    if os.path.isfile(d) or os.path.isdir(d):
        pwrap_error("ERROR: Cannot create '%s'--something is in the way." % d)
        return 0

    def _mkdir(d):
        if verbose:
            print "Creating '{0}'...".format(d)
        os.makedirs(d)

    def _copyfile(frompath, topath, fn):
        if verbose:
            print "Creating file '%s'..." % os.path.join(topath, fn)

        with open(os.path.join(frompath, fn), 'r') as fp:
            filedata = fp.readlines()

        fix = fn.endswith(('.ini', '.py', '.cgi', '.txt'))

        if fix:
            basedir = topath
            if not basedir.endswith(os.sep):
                basedir = basedir + os.sep
            if os.sep == "\\":
                basedir = basedir.replace(os.sep, os.sep + os.sep)
            datamap = {
                'basedir': basedir,
                'codedir': os.path.dirname(os.path.dirname(__file__))
            }
            filedata = [line % datamap for line in filedata]

        with open(os.path.join(topath, fn), 'w') as fp:
            fp.write(''.join(filedata))

    _mkdir(d)

    # Copy over data files
    source = os.path.join(os.path.dirname(__file__), 'data')
    for root, dirs, files in os.walk(source):
        dest = os.path.join(d, root[len(source)+1:])

        if not os.path.isdir(dest):
            if verbose:
                print "Creating '%s'..." % dest
            _mkdir(dest)

        for mem in files:
            _copyfile(root, dest, mem)

    datadir = os.path.join(d, "entries")
    firstpost = os.path.join(datadir, "firstpost.txt")
    if verbose:
        print "Creating file '%s'..." % firstpost
    datestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    fp = open(firstpost, "w")
    fp.write("""First post!
#published {0}
#tags firstpost
<p>
  This is your first post!  If you can see this with a web-browser,
  then it's likely that everything's working nicely!
</p>
""".format(datestamp))
    fp.close()

    if verbose:
        print "Done!"
    return 0


@with_config
def cmd_renderurl(cfg, command, argv):
    """Renders a single url of your blog."""
    parser = build_parser("%prog renderurl [options] <url> [<url>...]")

    parser.add_option("--headers",
                      action="store_true", dest="headers", default=False,
                      help="Option that causes headers to be displayed "
                      "when rendering a single url.")

    (options, args) = parser.parse_args(argv)

    if not args:
        parser.print_help()
        return 0

    for url in args:
        p = build_douglas(cfg)

        base_url = cfg.get('base_url', '')
        if url.startswith(base_url):
            url = url[len(base_url):]
        p.run_render_one(url, options.headers)

    return 0


@with_config
def cmd_staticrender(cfg, command, argv):
    """Statically renders your blog into an HTML site."""
    parser = build_parser("%prog staticrender [options]")
    parser.add_option("--incremental",
                      action="store_true", dest="incremental", default=False,
                      help="Option that causes static rendering to be "
                      "incremental.")

    (options, args) = parser.parse_args(argv)

    # Turn on memcache.
    from douglas import memcache
    memcache.usecache = True

    p = build_douglas(cfg)
    if not p:
        return 0

    return p.run_static_renderer(options.incremental)


DEFAULT_HANDLERS = [
    (key[4:], fun, fun.__doc__)
    for key, fun in globals().items()
    if key.startswith('cmd_')
]


def get_handlers(cfg):
    plugin_utils.initialize_plugins(
        cfg.get("plugin_dirs", []), cfg.get("load_plugins", []))

    handlers_dict = dict([(v[0], (v[1], v[2])) for v in DEFAULT_HANDLERS])
    handlers_dict = run_callback("commandline", handlers_dict,
                                 mappingfunc=lambda x, y: y,
                                 defaultfunc=lambda x: x)

    # test the handlers, drop any that aren't the right return type,
    # and print a warning.
    handlers = []
    for k, v in handlers_dict.items():
        if not len(v) == 2 or not callable(v[0]) or not isinstance(v[1], str):
            print "Plugin returned '%s' for commandline." % ((k, v),)
            continue
        handlers.append((k, v[0], v[1]))

    return sorted(handlers)


def main(argv):
    sys.path.append('.')

    # FIXME - rewrite with argparse
    if '--silent' in argv:
        sys.stdout = open(os.devnull, 'w')
        argv.remove('--silent')

    print 'douglas: version {0}'.format(__version__)

    # slurp off the config file setting and add it to sys.path.
    # this needs to be first to pick up plugin-based command handlers.
    configdir = None
    for i, mem in enumerate(argv):
        if mem.startswith('--config='):
            configflag, configdir = mem.split('=')
            argv.pop(i)
            break

        elif mem == '--config':
            try:
                configdir = argv[i+1]
                argv.pop(i)
                argv.pop(i)
                break
            except IndexError:
                return abort('Error: no config file argument specified.')

    if configdir is not None:
        if configdir.endswith("config.py"):
            configdir = configdir[:-9]

        if not os.path.exists(configdir):
            return abort('Error: "{0}" directory does not exist.'.format(
                configdir))

        if not os.path.exists(os.path.join(configdir, 'config.py')):
            return abort('Error: config.py not in "{0}".'.format(configdir))

        sys.path.insert(0, configdir)
        print 'Inserting {0} to beginning of sys.path....'.format(configdir)

    cfg = import_config(quiet=True)

    handlers = get_handlers(cfg)

    if not argv or argv == ['-h'] or argv == ['--help']:
        parser = build_parser('%prog [command]')
        parser.print_help()
        print ''
        print 'Commands:'
        for cmd_str, cmd_fun, cmd_hlp in handlers:
            print '    %-14s %s' % (cmd_str, cmd_hlp)
        print ''
        return 0

    if argv[0] == '--version':
        return 0

    command = argv.pop(0)
    for (c, f, h) in handlers:
        if c == command:
            return f(command, argv)

    pwrap_error('Command "{0}" does not exist.'.format(command))
    pwrap_error('')
    pwrap_error("Commands:")
    for cmd_str, cmd_fun, cmd_hlp in handlers:
        pwrap_error("    %-14s %s" % (cmd_str, cmd_hlp))
    return 1
