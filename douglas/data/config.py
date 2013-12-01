# -*- coding: utf-8 -*-
# =================================================================
# This is the config file for Douglas.  You should go through 
# this file and fill in values for the various properties.  This 
# affects the behavior of your blog.
#
# This is a Python code file and as such must be written in
# Python.
#
# There are configuration properties that are not detailed in
# this file.  These are the properties that are most often used.
# To see a full list of configuration properties as well as
# additional documentation, see the Douglas documentation on
# the web-site for your version of Douglas.
# =================================================================

# Don't touch this next line.
py = {}


# Codebase configuration
# ======================

# If you did not install Douglas as a library (i.e. python setup.py install)
# then uncomment this next line and point it to your Douglas installation
# directory.
# 
# Note, this should be the parent directory of the "Douglas" directory
# (note the case--uppercase P lowercase b!).
#py["codebase"] = "%(codedir)s"

import os

BLOGDIR = "%(basedir)s"

# Blog configuration
# ==================

# What is the title of this blog?
py["blog_title"] = "Another douglas blog"

# What is the description of this blog?
py["blog_description"] = "blosxom with a touch of python"

# Who are the author(s) of this blog?
py["blog_author"] = "name"

# What is the email address through which readers of the blog may contact
# the authors?
py["blog_email"] = "email@example.com"

# These are the rights you give to others in regards to the content
# on your blog.  Generally, this is the copyright information.
# This is used in the Atom feeds.  Leaving this blank or not filling
# it in correctly could result in a feed that doesn't validate.
py["blog_rights"] = "Copyright 2005 Joe Bobb"

# What is this blog's primary language? (For the RSS feed.)
py["blog_language"] = "en"

# Encoding for output.  This defaults to utf-8.
py["blog_encoding"] = "utf-8"

# What is the locale for this blog?  This is used when formatting dates
# and other locale-sensitive things.  Make sure the locale is valid for
# your system.  See the configuration chapter in the Douglas documentation
# for details.
#py["locale"] = "en_US.iso-8859-1"

# Where are this blog's entries kept?
py["datadir"] = os.path.join(BLOGDIR, "entries")

# Where are this blog's themes kept?
py["themedir"] = os.path.join(BLOGDIR, "themes")

# List of strings with directories that should be ignored (e.g. "CVS")
# ex: py['ignore_directories'] = ["CVS", "temp"]
py["ignore_directories"] = []

# Should I stick only to the datadir for items or travel down the directory
# hierarchy looking for items?  If so, to what depth?
# 0 = infinite depth (aka grab everything)
# 1 = datadir only
# n = n levels down
py["depth"] = 0

# How many entries should I show on the home page and category pages?
# If you put 0 here, then I will show all pages.
# Note: this doesn't affect date-based archive pages.
py["num_entries"] = 10

# What is the default theme you want to use when the user doesn't
# specify a theme in the request?
py["default_theme"] = "html"


# Logging configuration
# =====================

# Where should Douglas write logged messages to?
# If set to "NONE" log messages are silently ignored.
# Falls back to sys.stderr if the file can't be opened for writing.
#py["log_file"] = os.path.join(BLOGDIR, "logs", "douglas.log")

# At what level should we log to log_file?
# One of: "critical", "error", "warning", "info", "debug"
# For production, "warning" or "error' is recommended.
#py["log_level"] = "warning"


# Plugin configuration
# ====================

# Douglas comes with a set of plugins. If you want to use plugins
# that don't come with Douglas, including plugins that are in your
# blog's plugins/ directory, then you must list the directories
# those plugins are in with "plugin_dirs".
#
# Example: py['plugin_dirs'] = ["/home/joe/blog/plugins",
#                               "/var/lib/douglas/plugins"]
py["plugin_dirs"] = [os.path.join(BLOGDIR, "plugins")]

# Specify the plugins your blog uses here.  Plugins are specified
# by Python module name.  Plugins that come with Douglas all
# start with "douglas.plugins.<pluginname>".
# 
# If you specify an empty list, then this will load no plugins.
#
# For example:
# py["load_plugins"] = [
#     "douglas.plugins.paginate",
#     "douglas.plugins.tags",
#     "myfancyplugin"
# ]
py["load_plugins"] = [
    "douglas.plugins.paginate",
    "douglas.plugins.draft_folder",
    "douglas.plugins.pages",

    "douglas.plugins.tags",
    "douglas.plugins.yeararchives",

    "douglas.plugins.published_date",
]


# ======================
# Optional Configuration
# ======================

# What should this blog use as its base url?
#py["base_url"] = "http://www.example.com/weblog"

# Default parser/preformatter. Defaults to plain (does nothing)
#py["parser"] = "plain"



# Static rendering
# ================

# Doing static rendering?  Static rendering essentially "compiles" your
# blog into a series of static html pages.  For more details, see the
# documentation.
# 
# What directory do you want your static html pages to go into?
py["static_dir"] = os.path.join(BLOGDIR, "compiled_site")

# What themes should get generated?
py["static_themes"] = ["html"]

# What other paths should we statically render?
# This is for additional urls handled by other plugins like the booklist
# and plugin_info plugins.  If there are multiple themes you want
# to capture, specify each:
# ex: py["static_urls"] = ["/booklist.rss", "/booklist.html"]
# py["static_urls"] = ["/path/to/url1", "/path/to/url2"]

py["static_index_themes"] = ["html", "rss"]


# Whether (True) or not (False) you want to generate date indexes with month
# names?  (ex. /2004/Apr/01)  Defaults to True.
py["static_monthnames"] = False

# Whether (True) or not (False) you want to generate date indexes
# using month numbers?  (ex. /2004/04/01)  Defaults to False.
py["static_monthnumbers"] = False

# Whether (True) or not (False) you want to generate year indexes?
# (ex. /2004)  Defaults to True.
py["static_yearindexes"] = True


# Plugins
# =======

# tags
py["tags_separator"] = "::"

# draft_folder
py["draftdir"] = os.path.join(BLOGDIR, 'drafts')

# paginate
py['paginate_previous_text'] = "(more recent) &lt;&lt;"
py['paginate_next_text'] = "&gt;&gt; (less recent)"
py['paginate_count_from'] = 1
py['paginate_linkstyle'] = 1


# pages
py['pagesdir'] = os.path.join(BLOGDIR, 'pages')
py['pages_trigger'] = 'pages'
