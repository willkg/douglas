import os
import sys


class ConfigVariable(object):
    def __repr__(self):
        return 'ConfigVariable'

    def __str__(self):
        return str(self.value())

    def value(self):
        raise ValueError('Required value')

    def validate(self, value):
        # FIXME - This sort of works, but doesn't tell the user wtf
        # was actually wrong. Maybe validate should return None if
        # it's fine and a string with the error message if it's not
        # fine?
        return self._validate(value)


class Required(ConfigVariable):
    def __init__(self, validate=None):
        if validate is None:
            validate = lambda x: x
        self._validate = validate

    def __repr__(self):
        return 'Required'


class Optional(ConfigVariable):
    def __init__(self, default, validate=None):
        self._default = default
        if validate is None:
            validate = lambda x: True
        self._validate = validate

    def __repr__(self):
        return '(Optional) Default is {0}'.format(repr(self.value()))

    def value(self):
        return self._default


class Config(object):
    #: Set ``base_url`` in your ``config.py`` file to the base url for your
    #: blog. If someone were to type this url into their browser, they'd
    #: see the front page of your blog.
    #:
    #: .. Note::
    #: 
    #:    Your ``base_url`` property should **not** have a trailing slash.
    base_url = Required(validate=lambda x: x and not x.endswith('/'))

    #: This is the title of your blog.  Typically this should be short and
    #: is accompanied by a longer summary of your blog which is set in
    #: ``blog_description``.
    #:
    #: For example, if Joe were writing a blog about cooking, he might
    #: title his blog:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_title"] = "Joe's blog about cooking"
    blog_title = Optional('My blog')

    #: This is the description or byline of your blog.  Typically this is
    #: a phrase or a sentence that summarizes what your blog covers.
    #:
    #: If you were writing a blog about restaurants in the Boston area,
    #: you might have a ``blog_description`` of:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_description"] = "Critiques of restaurants in the Boston area"
    #:
    #:
    #: Or if your blog covered development on Douglas, your
    #: ``blog_description`` might go like this:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_description"] = (
    #:        "Ruminations on the development of Douglas and "
    #:        "related things that I discovered while working on "
    #:        "the project")
    blog_description = Optional('')

    #: This is the name of the author of your blog.  Very often this is
    #: your name or a pseudonym.
    #:
    #: If Joe Smith had a blog, he might set his ``blog_author`` to "Joe
    #: Smith":
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_author"] = "Joe Smith"
    #:
    #:
    #: If Joe Smith had a blog, but went by the pseudonym "Magic Rocks",
    #: he might set his ``blog_author`` to "Magic Rocks":
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_author"] = "Magic Rocks"
    blog_author = Optional('')

    #: This is the email address you want associated with your blog.
    #:
    #: For example, say Joe Smith had an email address
    #: ``joe@joesmith.net`` and wanted that associated with his blog.
    #: Then he would set the email address as such:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_email"] = "joe@joesmith.net"
    blog_email = Optional('')

    #: These are the rights you give to others in regards to the content
    #: on your blog. Generally this is the copyright information, for
    #: example:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_rights"] = "Copyright 2005 Joe Bobb"
    #:
    #: This is used in the Atom and RSS 2.0 feeds. Leaving this blank or
    #: not filling it in correctly could result in a feed that doesn't
    #: validate.
    blog_rights = Optional('')

    #: This is the primary language code for your blog.
    #:
    #: For example, English users should use ``en``:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_language"] = "en"
    #:
    #:
    #: This gets used in the RSS themes.
    #:
    #: Refer to `ISO 639-2`_ for language codes.  Many systems use
    #: two-letter ISO 639-1 codes supplemented by three-letter ISO 639-2
    #: codes when no two-letter code is applicable.  Often ISO 639-2 is
    #: sufficient.  If you use very special languages, you may want to
    #: refer to `ISO 639-3`_, which is a super set of ISO 639-2 and
    #: contains languages used thousands of years ago.
    #:
    #: .. _ISO 639-2: http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
    #: .. _ISO 639-3: http://www.sil.org/iso639-3/
    blog_language = Optional('')

    #: This is the character encoding of your blog.
    #:
    #: For example, if your blog was encoded in utf-8, then you would set
    #: the ``blog_encoding`` to:
    #:
    #: .. code-block:: python
    #:
    #:    py["blog_encoding"] = "utf-8"
    #:
    #:
    #: .. Note::
    #:
    #:    This value must be a valid character encoding value.  In
    #:    general, if you don't know what to set your encoding to then set
    #:    it to ``utf-8``.
    #:
    #: This value should be in the meta section of any HTML- or
    #: XHTML-based themes and it's also in the header for any feed-based
    #: themes.  An improper encoding will gummy up some/most feed readers
    #: and web-browsers.
    #:
    #: W3C has a nice `tutorial on encoding`_.  You may refer to `IANA
    #: charset registry`_ for a complete list of encoding names.
    #:
    #:
    #: .. _tutorial on encoding: http://www.w3.org/International/tutorials/tutorial-char-enc/
    #: .. _IANA charset registry: http://www.iana.org/assignments/character-sets
    blog_encoding = Optional('utf-8')

    #: This is the full path to where your blog entries are kept on the
    #: file system.
    #:
    #: For example, if you are storing your blog entries in
    #: ``/home/joe/blog/entries/``, then you would set the ``datadir``
    #: like this:
    #:
    #: .. code-block:: python
    #:
    #:    py["datadir"] = "/home/joe/blog/entries/"
    #:
    #: .. Note::
    #:
    #:    Must not end with a /.
    datadir = Required(validate=lambda x: x and os.path.isdir(x) and not x.endswith('/'))

    #: The depth setting determines how many levels deep in the directory
    #: (category) tree that Douglas will display when doing indexes.
    #:
    #: * 0 - infinite depth (aka grab everything) DEFAULT
    #: * 1 - datadir only
    #: * 2 - two levels
    #: * 3 - three levels
    #: * ...
    #: * *n* - *n* levels deep
    depth = Optional(0, lambda x: isinstance(x, int))

    #: The ``renderer`` variable lets you specify which renderer to use.
    renderer = Optional('jinjarenderer')

    #: The ``ignore_directories`` variable allows you to specify which
    #: directories in your datadir should be ignored by Douglas.
    #:
    #: This defaults to an empty list (i.e. Douglas will not ignore any
    #: directories).
    #:
    #: For example, if you use CVS to manage the entries in your datadir,
    #: then you would want to ignore all CVS-related directories like
    #: this::
    #:
    #:    py["ignore_directories"] = ["CVS"]
    #:
    #:
    #: If you were using CVS and you also wanted to store drafts of
    #: entries you need to think about some more in a drafts directory in
    #: your datadir, then you could set your ``ignore_directories`` like
    #: this::
    #:
    #:    py["ignore_directories"] = ["drafts", "CVS"]
    #:
    #:
    #: This would ignore all directories named "CVS" and "drafts" in your
    #: datadir tree.
    ignore_directories = Optional([], lambda x: isinstance(x, (tuple, list)))

    #: This is the full path to where your Douglas themes are kept.
    #:
    #: If you do not set the ``themedir``, then Douglas will look for your
    #: themes and templates in the datadir alongside your entries.
    #:
    #: .. Note::
    #:
    #:    "theme" is spelled using the British spelling and not the
    #:    American one.
    #:
    #: For example, if you want to put your entries in
    #: ``/home/joe/blog/entries/`` and your theme templates in
    #: ``/home/joe/blog/themes/`` you would set ``themedir`` and
    #: ``datadir`` like this::
    #:
    #:    py["datadir"] = "/home/joe/blog/entries/"
    #:    py["themedir"] = "/home/joe/blog/themes/"
    themedir = Required(lambda x: os.path.isdir(x))

    #: This specified the theme that will be used if the user doesn't
    #: specify a theme in the URI.
    #:
    #: For example, if you wanted your default theme to be "joy", then
    #: you would set ``default_theme`` like this::
    #:
    #:    py["default_theme"] = "joy"
    #:
    #:
    #: Doing this will cause Douglas to use the "joy" theme whenever
    #: URIs are requested that don't specify the theme.
    #:
    #: For example, the following will all use the "joy" theme::
    #:
    #:    http://example.com/blog/
    #:    http://example.com/blog/index
    #:    http://example.com/blog/movies/
    #:    http://example.com/blog/movies/supermanreturns
    default_theme = Optional('html')

    #: The ``num_entries`` variable specifies the number of entries that
    #: show up on your home page and other category index pages.  It
    #: doesn't affect the number of entries that show up on date-based
    #: archive pages.
    #:
    #: It defaults to 5 which means "show at most 5 entries".
    #:
    #: If you set it to 0, then it will show all entries that it can.
    #:
    #: For example, if you wanted to set ``num_entries`` to 10 so that 10
    #: entries show on your category index pages, you sould set it like
    #: this::
    #:
    #:    py["num_entries"] = 10
    num_entries = Optional(10, lambda x: isinstance(x, int))

    #: Whether or not to truncate the number of entries displayed on teh
    #: front page to ``num_entries`` number of entries.
    #:
    #: For example, this causes all entries to be displayed on your front
    #: page (which is probably a terrible idea):
    #:
    #: .. code-block:: python
    #:
    #:    py["truncate_frontpage"] = False
    truncate_frontpage = Optional(True, lambda x: isinstance(x, bool))

    #: Whether or not to truncate the number of entries displayed on a
    #: category-based index page to ``num_entries`` number of entries.
    #:
    #: For example, this causes all entries in a category to show up in
    #: all category-based index pages:
    #:
    #: .. code-block:: python
    #:
    #:    py["truncate_category"] = False
    truncate_category = Optional(True, lambda x: isinstance(x, bool))

    #: Whether or not to truncate the number of entries displayed on a
    #: date-based index page to ``num_entries`` number of entries.
    truncate_date = Optional(False, lambda x: isinstance(x, bool))

    #: Lets you override which file extensions are parsed by which entry
    #: parsers. The keys are the file extension. The values are the Python
    #: module path to the callable that will parse the file.
    #: 
    #: For example, by default, the blosxom_entry_parser parses files
    #: ending with ``.txt``. You can also have it parse files ending in
    #: ``.html``::
    #: 
    #:     py["entryparsers"] = {
    #:         'html': 'douglas.app:blosxom_entry_parser'
    #:     }
    #: 
    #: The ``douglas.app`` part denotes which Python module the callable is in.
    #: The ``blosxom_entry_parser`` part is the name of a function in the
    #: ``douglas.app`` module which will parse the entry.
    entryparsers = Optional({}, lambda x: isinstance(x, dict))

    #: This specifies the file that Douglas will log messages to.
    #: 
    #: If Douglas cannot open the file for writing, then log messages
    #: will be sent to sys.stderr.
    #: 
    #: For example, if you wanted Douglas to log messages to
    #: ``/home/joe/blog/logs/douglas.log``, then you would set
    #: ``log_file`` to::
    #: 
    #:    py["log_file"] = "/home/joe/blog/logs/douglas.log"
    #: 
    #: If you were on Windows, then you might set it to::
    #: 
    #:    py["log_file"] = "c:/blog/logs/douglas.log"
    #: 
    #: .. Note::
    #: 
    #:    The web server that is executing Douglas must be able to write
    #:    to the directory containing your ``douglas.log`` file.
    log_file = Optional(sys.stderr)

    #: This is based on the Python logging module, so the levels are the
    #: same:
    #: 
    #: * ``critical``
    #: * ``error``
    #: * ``warning``
    #: * ``info``
    #: * ``debug``
    #: 
    #: This sets the log level for logging messages.
    #: 
    #: If you set the ``log_level`` to ``critical``, then *only* critical
    #: messages are logged.
    #: 
    #: If you set the ``log_level`` to ``error``, then error and critical
    #: messages are logged.
    #: 
    #: If you set the ``log_level`` to ``warning``, then warning, error,
    #: and critical messages are logged.
    #: 
    #: So on and so forth.
    #: 
    #: For "production" blogs (i.e. you're not tinkering with
    #: configuration, new plugins, new themes, or anything along those
    #: lines), then this should be set to ``warning`` or ``error``.
    #: 
    #: For example, if you're done tinkering with your blog, you might set
    #: the ``log_level`` to ``info`` allowing you to see how requests are
    #: being processed::
    #: 
    #:    py['log_level'] = "info"
    log_level = Optional('error')


    #: The ``plugin_dirs`` variable tells Douglas which directories
    #: to look for plugins in addition to the plugins that Douglas comes
    #: with. You can list as many directories as you want.
    #: 
    #: For example, if your blog used the "paginate" plugin that comes
    #: with Douglas and a "myfancyplugin" that you wrote yourself
    #: that's in your blog's plugins directory, then you might set
    #: ``plugin_dirs`` like this::
    #: 
    #:    py["plugin_dirs"] = [
    #:        "/home/joe/blog/plugins/"
    #:    ]
    #: 
    #: .. Note::
    #: 
    #:    Plugin directories are not searched recursively for plugins.  If
    #:    you have a tree of plugin directories that have plugins in them,
    #:    you'll need to specify each directory in the tree.
    #: 
    #:    For example, if you have plugins in ``~/blog/my_plugins/`` and
    #:    ``~/blog/phils_plugins/``, then you need to specify both
    #:    directories in ``plugin_dirs``::
    #: 
    #:       py["plugin_dirs"] = [
    #:           "/home/joe/blog/my_plugins",
    #:           "/home/joe/blog/phils_plugins"
    #:           ]
    #: 
    #:    You can't just specify ``~/blog/`` and expect Douglas to find
    #:    the plugins in the directory tree::
    #: 
    #:       # This won't work!
    #:       py["plugin_dirs"] = [
    #:           "/home/joe/blog"
    #:           ]
    #: 
    #: 
    #: .. Note::
    #: 
    #:    Plugins that come with Douglas are automatically found---you
    #:    don't have to specify anything in your``plugin_dirs`` in order
    #:    to use core plugins.
    plugin_dirs = Optional([], lambda x: isinstance(x, (tuple, list)))

    #: Specifying ``load_plugins`` causes Douglas to load only the plugins
    #: you name and in in the order you name them.
    #: 
    #: The value of ``load_plugins`` should be a list of strings where
    #: each string is the name of a Python module.
    #: 
    #: If you specify an empty list no plugins will be loaded.
    #: 
    #: .. Note::
    #: 
    #:    Douglas loads plugins in the order specified by
    #:    ``load_plugins``.  This order also affects the order that
    #:    callbacks are registered and later executed.  For example, if
    #:    ``plugin_a`` and ``plugin_b`` both implement the ``handle``
    #:    callback and you load ``plugin_b`` first, then ``plugin_b`` will
    #:    execute before ``plugin_a`` when the ``handle`` callback kicks
    #:    off.
    #: 
    #:    Usually this isn't a big deal, however it's possible that some
    #:    plugins will want to have a chance to do things before other
    #:    plugins.  This should be specified in the documentation that
    #:    comes with those plugins.
    load_plugins = Optional([], lambda x: isinstance(x, (tuple, list)))

    #: This is the directory we will save all the output.  The value of
    #: ``compiledir`` should be a string representing the **absolute
    #: path** of the output directory for compiling.
    #: 
    #: For example, Joe puts the output in his ``public_html`` directory
    #: of his account:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["compiledir"] = "/home/joe/public_html"
    compiledir = Optional('', lambda x: os.path.isdir(x))

    #: The value of ``compile_themes`` should be a list of strings
    #: representing all the themes that should be rendered.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["compile_themes"] = ["html"]
    compile_themes = Optional(['html'], lambda x: isinstance(x, (tuple, list)))

    #: ``compile_index_themes`` is just like ``compile_themes`` except
    #: it's the themes of the index files: frontpage index, category
    #: indexes, date indexes, ...
    #: 
    #: Defaults to ``["html"]`` which only renders the html theme.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["compile_index_themes"] = ["html"]
    #: 
    #: 
    #: If you want your index files to also be feeds, then you should add
    #: a feed theme to the list.
    compile_index_themes = Optional(['html'], lambda x: isinstance(x, (tuple, list)))

    #: Whether or not to generate indexes per day.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["day_indexes"] = True
    day_indexes = Optional(False, lambda x: isinstance(x, bool))

    #: Whether or not to generate indexes per month.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["month_indexes"] = True
    month_indexes = Optional(False, lambda x: isinstance(x, bool))

    #: Whether or not to generate indexes per year.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["year_indexes"] = True
    year_indexes = Optional(True, lambda x: isinstance(x, bool))

    #: Any other url paths to compile.  Sometimes plugins require you to
    #: add additional paths---this is where you'd do it.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py["compile_urls"] = [
    #:        "/booklist"
    #:    ]
    compile_urls = Optional([], lambda x: isinstance(x, (tuple, list)))

    #: The url where your static assets will be.
    #: 
    #: If you're using a CDN, this is the CDN url.
    #: 
    #: If you're not using a CDN, this is probably the :confval:`base_url`
    #: plus ``/static``.
    #: 
    #: You can use this variable in your templates. For example:
    #: 
    #: .. code-block:: html
    #: 
    #:    <link rel="stylesheet" href="{{ static_url }}/css/style.css">
    static_url = Optional('')

    #: Any additional directories you want copied over to the compiledir.
    #: 
    #: For example:
    #: 
    #: .. code-block:: python
    #: 
    #:    py['static_files_dirs'] = [
    #:        '/home/joe/blog/staticimages/',
    #:        '/home/joe/blog/blogimages/'
    #:    ]
    static_files_dirs = Optional([], lambda x: isinstance(x, (tuple, list)))

    @classmethod
    def validate(cls, cfg):
        new_cfg = {}

        configvars = [mem for mem in dir(cls)
                      if isinstance(getattr(cls, mem), ConfigVariable)]

        for key in configvars:
            cvar = getattr(Config, key)

            if isinstance(cvar, Required) and key not in cfg:
                raise ValueError('{0} missing from config'.format(repr(key)))

            if key in cfg:
                if not cvar.validate(cfg[key]):
                    raise ValueError('{0} has bad value {1}'.format(
                        repr(key), repr(cfg[key])))
            else:
                # Seed the new_cfg with the default values
                new_cfg[key] = cvar.value()

        # Add everything from config.py to the config
        new_cfg.update(cfg)

        return new_cfg


def import_config():
    from config import py as cfg
    return Config.validate(cfg)
