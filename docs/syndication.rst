===========
Syndication
===========

Summary
=======

Syndicating your blog is very important as it provides a mechanism for
readers of your blog to keep up to date.  Typically this is done with
newsreader software.  Additionally, there are websites that post blog
entries from a variety of blogs that have similar content.  Both
newsreaders and planet-type websites need a semantically marked up
version of your blog.

Most newsreaders read most of the syndication formats.  So you
shouldn't feel that you have to implement each one of them in your
blog---you can most assuredly get away with just having RSS 2.0.

The syndication themes that come with Douglas should be fine for
most blogs.  When pointing people to your syndication feed, just use
one of the syndication themes.

Examples:

* ``http://example.com/blog/index.rss``



Feed formats that come with Douglas
===================================

Douglas comes with RSS 2.0 feed format.  If it's missing features
that you want (for example, some folks are doing podcasting with
their blog), then override the individual templates you need to
adjust.

For more information on RSS 2.0, see the `RSS 2.0 spec`_.

.. _RSS 2.0 spec: http://blogs.law.harvard.edu/tech/rss


Debugging your feeds
====================

`FeedValidator`_ is a useful tool for figuring out whether your
feed is valid and fixing bugs in your feed content.

.. _FeedValidator: http://feedvalidator.org/

Additionally, feel free to ask on the douglas-users mailing list.
