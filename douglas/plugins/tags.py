"""
Summary
=======

This plugin allows you to specify the tags your entry has in the
metadata of the entry.  It adds a new command to douglas-cmd to index
all the tags data and store it in a file.

It creates a ``TagManager`` instance in the Jinja2 environment which
you can use to iterate through and display tags data.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.tags`` to the ``load_plugins`` list in your
   ``config.py`` file.

2. Configure as documented below.


Configuration
=============

The following config properties define where the tags file is located,
how tag metadata is formatted, and how tag lists triggered.

``tags_separator``

    This defines the separator between tags in the metadata line.
    Defaults to ",".

    After splitting on the separator, each individual tag is stripped
    of whitespace before and after the text.

    For example::

       Weather in Boston
       #tags weather, boston
       <p>
         The weather in Boston today is pretty nice.
       </p>

    returns tags ``weather`` and ``boston``.

    If the ``tags_separator`` is::

       py["tags_separator"] = "::"

    then tags could be declared in the entries like this::

       Weather in Boston
       #tags weather::boston
       <p>
         The weather in Boston today is pretty nice.
       </p>

``tags_filename``

    This is the file that holds indexed tags data.  Defaults to
    datadir + os.pardir + ``tags.index``.

    This file needs to be readable by the process that runs your blog.
    This file needs to be writable by the process that creates the
    index.

``tags_trigger``

    This is the url trigger to indicate that the tags plugin should
    handle the file list based on the tag.  Defaults to ``tag``.

``truncate_tags``

    If this is True, then tags index listings will get passed through
    the truncate callback.  If this is False, then the tags index
    listing will not be truncated.

    If you're using a paging plugin, then setting this to True will
    allow your tags index to be paged.

    Example::

        py["truncate_tags"] = True

    Defaults to True.


Usage in templates
==================

The ``TagManager`` has the following methods:

``all_tags()``
    Returns a list of (tag, tag_url, count) tuples.

    You can iterate over this to render tag data for all the tags
    on your blog.

``all_tags_div()``
    Generates HTML for a div of class ``allTags`` with ``a`` tags of
    class ``tag`` in it--one for each tag.

``all_tags_cloud()``
    Generates HTML for a div of class ``allTagsCloud`` with ``a`` tags
    of class ``tag`` in it--one for each tag. The ``a`` tags also have
    one of ``biggestTag``, ``bigTag``, ``mediumTag``, ``smallTag``, or
    ``smallestTag`` depending on how "big" the tag should show up in
    the cloud.

``entry_tags(entry)``
    Returns a list of (tag, tag_url) tuples for tags for the specified
    entry.

``entry_tags_span(entry)``
    Generates HTML for a span of class ``entryTags`` with ``a`` tags
    of class ``tag`` in it--one for each tag.


.. Note::

   If you use functions that generate HTML in a Jinja2 template, you
   need to run them through the ``|safe`` filter. Otherwise the HTML
   will be escaped.


Creating the tags index file
============================

Run::

    douglas-cmd buildtags

from the directory your ``config.py`` is in or::

    douglas-cmd buildtags --config=/path/to/config/file

from anywhere.

This builds the tags index file that the tags plugin requires to
generate tags-based bits for the request.

Until you rebuild the tags index file, the entry will not have its
tags indexed.  Thus you should either rebuild the tags file after writing
or updating an entry or you should rebuild the tags file as a cron job.

.. Note::

   If you're compiling your blog, you need to build the tags index
   before you compile.


Converting from categories to tags
==================================

This plugin has a command that goes through your entries and adds tag
metadata based on the category.  There are some caveats:

1. it assumes entries are in the blosxom format of title, then
   metadata, then the body.

2. it only operates on entries in the datadir.

It maintains the atime and mtime of the file.  My suggestion is to
back up your files (use tar or something that maintains file stats),
then try it out and see how well it works, and figure out if that
works or not.

To run the command do::

    douglas-cmd categorytotags

from the directory your ``config.py`` is in or::

    douglas-cmd categorytotags --config=/path/to/config/file

from anywhere.

"""

__description__ = "Tags plugin"
__category__ = "tags"
__license__ = "MIT"


import cPickle as pickle
import os
import shutil

from douglas.memcache import memcache_decorator


def savefile(path, tagdata):
    """Saves tagdata to file at path."""
    with open(path + '.new', 'w') as fp:
        pickle.dump(tagdata, fp)
    shutil.move(path + '.new', path)


@memcache_decorator('tags')
def loadfile(path):
    """Loads tagdata from file at path."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as fp:
        tagdata = pickle.load(fp)
    return tagdata


def get_tagsfile(cfg):
    """Generates tagdata filename."""
    tagsfile = cfg.get('tags_filename',
                       os.path.join(cfg['datadir'], os.pardir, 'tags.index'))
    return tagsfile


def cmd_buildtags(command, argv):
    """Command for building the tags index."""
    from config import py as cfg

    datadir = cfg.get('datadir')
    if not datadir:
        raise ValueError('config.py has no datadir property.')

    sep = cfg.get('tags_separator', ',')
    tagsfile = get_tagsfile(cfg)

    from douglas import tools
    from douglas.app import Douglas, initialize
    from douglas.entries import fileentry

    # Build a douglas object, initialize it, and run the start
    # callback.  This gives entry parsing related plugins a chance to
    # get their stuff together so that they work correctly.
    initialize(cfg)
    p = Douglas(cfg, {})
    p.initialize()
    req = p.get_request()
    tools.run_callback("start", {"request": req})

    # Grab all the entries in the datadir
    entrylist = [fileentry.FileEntry(req, e, datadir)
                 for e in tools.get_entries(cfg, datadir)]

    tags_to_files = {}
    for mem in entrylist:
        tagsline = mem["tags"]
        if not tagsline:
            continue
        tagsline = [t.strip() for t in tagsline.split(sep)]
        for t in tagsline:
            tags_to_files.setdefault(t, []).append(mem["filename"])

    savefile(tagsfile, tags_to_files)
    return 0


def cmd_category_to_tags(command, argv):
    """Goes through all entries and converts the category to tags
    metadata.

    It adds the tags line as the second line.

    It maintains the mtime for the file.
    """
    from config import py as cfg

    datadir = cfg.get("datadir")
    if not datadir:
        raise ValueError("config.py has no datadir property.")

    sep = cfg.get("tags_separator", ",")

    from douglas import tools
    from douglas.app import initialize

    initialize(cfg)
    filelist = tools.get_entries(cfg, datadir)

    if not datadir.endswith(os.sep):
        datadir = datadir + os.sep

    for mem in filelist:
        print "working on %s..." % mem

        category = os.path.dirname(mem)[len(datadir):]
        tags = category.split(os.sep)
        print "   adding tags %s" % tags
        tags = "#tags %s\n" % (sep.join(tags))

        atime, mtime = os.stat(mem)[7:9]

        with open(mem, 'r') as fp:
            data = fp.readlines()

        data.insert(1, tags)

        with open(mem, 'w') as fp:
            fp.write("".join(data))

        os.utime(mem, (atime, mtime))

    return 0


def cb_commandline(args):
    args['buildtags'] = (cmd_buildtags, 'builds the tags index')
    args['categorytotags'] = (
        cmd_category_to_tags,
        'builds tag metadata from categories for entries')
    return args


# FIXME - Probably can nix this and have everything call loaddata.
def cb_start(args):
    request = args['request']
    data = request.get_data()
    tagsfile = get_tagsfile(request.get_configuration())
    if os.path.exists(tagsfile):
        try:
            tagsdata = loadfile(tagsfile)
        except IOError:
            tagsdata = {}
    else:
        tagsdata = {}
    data['tagsdata'] = tagsdata


def cb_filelist(args):
    from douglas import tools
    from douglas.app import blosxom_truncate_list_handler

    # Handles /trigger/tag to show all the entries tagged that way
    req = args['request']

    pyhttp = req.get_http()
    data = req.get_data()
    config = req.get_configuration()

    trigger = '/' + config.get('tags_trigger', 'tag')
    if not pyhttp['PATH_INFO'].startswith(trigger):
        return

    datadir = config['datadir']
    tagsfile = get_tagsfile(config)
    tagsdata = loadfile(tagsfile)

    tag = pyhttp['PATH_INFO'][len(trigger)+1:]
    filelist = tagsdata.get(tag, [])
    if not filelist:
        tag, ext = os.path.splitext(tag)
        filelist = tagsdata.get(tag, [])
        if filelist:
            data['theme'] = ext[1:]

    from douglas.entries import fileentry
    entrylist = [fileentry.FileEntry(req, e, datadir) for e in filelist]

    # sort the list by mtime
    entrylist.sort(key=lambda entry: entry._mtime, reverse=True)

    data['truncate'] = config.get('truncate_tags', True)

    args = {'request': req, 'entry_list': entrylist}
    entrylist = tools.run_callback('truncatelist',
                                   args,
                                   donefunc=lambda x: x != None,
                                   defaultfunc=blosxom_truncate_list_handler)

    return entrylist


class TagManager(object):
    def __init__(self, request):
        self.request = request
        self._tagsdata = None

    @property
    def tagsdata(self):
        if self._tagsdata is None:
            tagsfile = get_tagsfile(self.request.get_configuration())
            if os.path.exists(tagsfile):
                try:
                    tagsdata = loadfile(tagsfile)
                except IOError:
                    tagsdata = {}
            else:
                tagsdata = {}
            self._tagsdata = tagsdata
        return self._tagsdata

    def all_tags(self):
        """Returns list of (tag, tag_url, count) tuples"""
        theme = self.request.get_theme()
        cfg = self.request.get_configuration()
        baseurl = cfg.get('base_url', '')
        trigger = cfg.get('tags_trigger', 'tag')

        tags = [
            (tag,
             '/'.join([baseurl.rstrip('/'), trigger, tag]) + '.' + theme,
             len(entries))
            for tag, entries in self.tagsdata.items()]

        return tags

    def all_tags_div(self):
        """Generates div version of all tags"""
        start_t = '<div class="allTags">'
        item_t = ' <a class="tag" href="{0}">{1}</a> '
        finish_t = '</div>'

        output = [start_t]
        for tag, tag_url, count in self.all_tags():
            output.append(item_t.format(tag_url, tag))
        output.append(finish_t)
        return '\n'.join(output)

    def all_tags_cloud(self):
        """Generates div tag cloud of all tags"""
        start_t = '<div class="allTagsCloud">'
        item_t = '<a class="tag {0}" href="{1}">{2}</a>'
        finish_t = '</div>'

        all_tags = self.all_tags()

        tagcloud = [start_t]
        if all_tags:
            all_tags.sort(key=lambda x: x[2])
            # the most popular tag is at the end--grab the number of files
            # that have that tag
            max_count = all_tags[-1][2]
            min_count = all_tags[0][2]

            # figure out the bin size for the tag size classes
            b = (max_count - min_count) / 5

            range_and_class = (
                (min_count + (b * 4), 'biggestTag'),
                (min_count + (b * 3), 'bigTag'),
                (min_count + (b * 2), 'mediumTag'),
                (min_count + b, 'smallTag'),
                (0, 'smallestTag')
            )

            all_tags.sort()

            for tag, tag_url, count in all_tags:
                for tag_range, tag_size_class in range_and_class:
                    if count > tag_range:
                        tag_class = tag_size_class
                        break
                tagcloud.append(item_t.format(tag_class, tag_url, tag))

        tagcloud.append(finish_t)
        return '\n'.join(tagcloud)

    def entry_tags(self, entry):
        """Returns list of (tag, tag_url) tuples for this entry"""
        cfg = self.request.get_configuration()

        sep = cfg.get('tags_seperator', ',')
        tags = sorted([t.strip() for t in entry.get('tags', '').split(sep)])
        theme = self.request.get_theme()
        baseurl = cfg.get('base_url', '')
        trigger = cfg.get('tags_trigger', 'tag')

        return [
            (tag,
             '/'.join([baseurl.rstrip('/'), trigger, tag]) + '.' + theme)
            for tag in tags]

    def entry_tags_span(self, entry):
        """Returns span version of entry tags"""
        start_t = '<span class="entryTags">'
        item_t = ' <a class="tag" href="{0}">{1}</a> '
        finish_t = '</span>'

        output = [start_t]
        for tag, tag_url in self.entry_tags(entry):
            output.append(item_t.format(tag_url, tag))
        output.append(finish_t)
        return '\n'.join(output)


def cb_context_processor(args):
    context = args['context']
    request = args['request']
    context['tags'] = TagManager(request)
    return args


def cb_compile_filelist(args):
    req = args["request"]

    # We call our own cb_start() here because we need to initialize
    # the tagsdata.
    cb_start({"request": req})

    config = req.get_configuration()
    filelist = args["filelist"]

    tagsdata = req.get_data()["tagsdata"]
    index_themes = config.get("compile_index_themes", ["html"])
    trigger = "/" + config.get("tags_trigger", "tag")

    # Go through and add an index for each index_theme for each tag.
    for tag in tagsdata.keys():
        for theme in index_themes:
            filelist.append((trigger + "/" + tag + "." + theme, ""))
