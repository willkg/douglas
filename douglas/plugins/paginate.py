"""
Summary
=======

Plugin for paging long index pages.

douglas uses the ``num_entries`` configuration variable to prevent
more than ``num_entries`` being rendered by cutting the list down to
``num_entries`` entries.  So if your ``num_entries`` is set to 20, you
will only see the first 20 entries rendered.

The paginate plugin overrides this functionality and allows for
paging.


Install
=======

This plugin comes with douglas.  To install, do the following:

1. Add ``douglas.plugins.paginate`` to your ``load_plugins`` list
   variable in your ``config.py`` file.

   Make sure it's the first plugin in the ``load_plugins`` list so
   that it has a chance to operate on the entry list before other
   plugins.

2. (optional) Add some configuration to your ``config.py`` file.

3. Add the following blurb where you want page navigation to your
   entry_list template::

       <p>
         {{ page_navigation|safe }}
       </p>


Configuration variables
=======================

``paginate_previous_text``

   Defaults to "&lt;&lt;".

   This is the text for the "previous page" link.


``paginate_next_text``

   Defaults to "&gt;&gt;".

   This is the text for the "next page" link.


``paginate_linkstyle``

   Defaults to 1.

   This allows you to change the link style of the paging.

   Style 0::

       [1] 2 3 4 5 6 7 8 9 ... >>

   Style 1::

      Page 1 of 4 >>

   If you want a style different than that, you'll have to copy the
   plugin and implement your own style.


Note about static rendering
===========================

This plugin works fine with static rendering, but the urls look
different. Instead of adding a ``page=4`` kind of thing to the
querystring, this adds it to the url.

For example, say your front page was ``/index.html`` and you had 5
pages of entries. Then the urls would look like this::

    /index.html           first page
    /index_page2.html     second page
    /index_page3.html     third page
    ...

"""

__description__ = (
    'Allows navigation by page for indexes that have too many entries.')
__category__ = 'display'
__license__ = 'MIT'


import os

from douglas.tools import pwrap_error, render_url_statically


def verify_installation(request):
    config = request.get_configuration()
    if config.get('num_entries', 0) == 0:
        pwrap_error(
            'Missing config property "num_entries".  paginate won\'t do '
            'anything without num_entries set.  Either set num_entries '
            'to a positive integer, or disable the paginate plugin.'
            'See the documentation at the top of the paginate plugin '
            'code file for more details.')
        return False
    return True


class PageDisplay:
    def __init__(self, url_template, url_template_n, current_page, max_pages,
                 count_from, previous_text, next_text, linkstyle):
        self.url_template = url_template
        self.url_template_n = url_template_n
        self.current_page = current_page
        self.max_pages = max_pages
        self.count_from = count_from
        self.previous_text = previous_text
        self.next_text = next_text
        self.linkstyle = linkstyle

    def __str__(self):
        # FIXME - turn this into unicode
        output = []
        # prev
        if self.current_page != self.count_from:
            if self.current_page - 1 == 1:
                prev_url = self.url_template
            else:
                prev_url = self.url_template_n % (self.current_page - 1)
            output.append('<a href="%s">%s</a>&nbsp;' %
                          (prev_url, self.previous_text))

        # pages
        if self.linkstyle == 0:
            for i in range(self.count_from, self.max_pages):
                if i == self.current_page:
                    output.append('[%d]' % i)
                else:
                    page_url = self.url_template_n % i
                    output.append('<a href="%s">%d</a>' % (page_url, i))

        elif self.linkstyle == 1:
            output.append(' Page %s of %s ' %
                          (self.current_page, self.max_pages - 1))

        # next
        if self.current_page < self.max_pages - 1:
            next_url = self.url_template_n % (self.current_page + 1)
            output.append('&nbsp;<a href="%s">%s</a>' %
                          (next_url, self.next_text))

        return ' '.join(output)


def page(request, num_entries, entry_list):
    http = request.get_http()
    config = request.get_configuration()
    data = request.get_data()

    previous_text = config.get('paginate_previous_text', '&lt;&lt;')
    next_text = config.get('paginate_next_text', '&gt;&gt;')

    linkstyle = config.get('paginate_linkstyle', 1)
    if linkstyle > 1:
        linkstyle = 1

    entries_per_page = num_entries
    count_from = 1

    if (entries_per_page <= 0
        or not isinstance(entry_list, list)
        or len(entry_list) <= entries_per_page):

        return

    page = count_from
    url = http.get('REQUEST_URI', http.get('HTTP_REQUEST_URI', ''))
    url_template = url

    if data.get('STATIC'):
        # This is the static rendering case, so we have to do some
        # fancy footwork to get this to work correctly.

        try:
            page = data['paginate_page']
        except KeyError:
            page = count_from

        # The REQUEST_URI isn't the full url here--it's only the
        # path and so we need to add the base_url.
        base_url = config['base_url'].rstrip('/')
        url_template = base_url + url_template
        url_template = url_template.split('/')

        last_part = url_template[-1]
        if '_' in last_part:
            # We need to get the filename and the extension and
            # ignore the page number here.
            fn, pageno = last_part.rsplit('_', 1)
            pageno, ext = os.path.splitext(pageno)

        else:
            # This has no page number, yet.
            fn, ext = os.path.splitext(last_part)

        pageno_template = '_page%d'

        last_part = fn + pageno_template + ext
        url_template_n = '/'.join(url_template[:-1]) + '/' + last_part
        url_template = '/'.join(url_template[:-1]) + '/' + fn + ext

    else:
        form = request.get_form()

        if form:
            try:
                page = int(form.getvalue('page'))
            except (TypeError, ValueError):
                pass

        # Restructure the querystring so that page= is at the end
        # where we can fill in the next/previous pages.
        if url_template.find('?') != -1:
            url_template, query = url_template.split('?', 1)
            query = query.split('&')
            query = [m for m in query if not m.startswith('page=')]

        else:
            query = []

        query = '&'.join(query + ['page=%d'])
        url_template = url_template + '?' + query
        url_template_n = url_template

    begin = (page - count_from) * entries_per_page
    end = (page + 1 - count_from) * entries_per_page
    if end > len(entry_list):
        end = len(entry_list)

    max_pages = ((len(entry_list) - 1) / entries_per_page) + 1 + count_from

    data['entry_list'] = entry_list[begin:end]

    data['page_navigation'] = PageDisplay(
        url_template, url_template_n, page, max_pages, count_from, previous_text,
        next_text, linkstyle)

    # If we're static rendering and there wasn't a page specified
    # and this is one of the themes to statically render, then
    # this is the first page and we need to render all the rest of
    # the pages, so we do that here.
    static_themes = config.get('static_themes', ['html'])
    if ((data.get('STATIC') and page == count_from
         and data.get('theme') in static_themes)):
        # Turn http://example.com/index.html into
        # http://example.com/index_page5.html for each page.
        url = url.split('/')
        fn = url[-1]
        fn, ext = os.path.splitext(fn)
        template = '/'.join(url[:-1]) + '/' + fn + '_page%d'
        if ext:
            template = template + ext

        for i in range(count_from + 1, max_pages):
            print '   rendering page %s ...' % (template % i)
            render_url_statically(dict(config), template % i, '')


def cb_truncatelist(args):
    request = args['request']
    entry_list = args['entry_list']

    page(request, request.config.get('num_entries', 10), entry_list)
    return request.data.get('entry_list', entry_list)


def cb_pathinfo(args):
    request = args['request']
    data = request.get_data()

    # This only kicks in during static rendering.
    if not data.get('STATIC'):
        return

    http = request.get_http()
    pathinfo = http.get('PATH_INFO', '').split('/')

    # Handle the http://example.com/index_page5.html case. If we see
    # that, put the page information in the data dict under
    # 'paginate_page' and 'fix' the pathinfo.
    if pathinfo and '_page' in pathinfo[-1]:
        fn, pageno = pathinfo[-1].rsplit('_', 1)
        pageno, ext = os.path.splitext(pageno)
        try:
            pageno = int(pageno[4:])
        except (ValueError, TypeError):
            # If it's not a valid page number, then we shouldn't be
            # doing anything here.
            return

        pathinfo[-1] = fn
        pathinfo = '/'.join(pathinfo)
        if ext:
            pathinfo += ext

        http['PATH_INFO'] = pathinfo
        data['paginate_page'] = pageno