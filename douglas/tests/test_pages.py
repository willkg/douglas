import os
from textwrap import dedent

from nose.tools import eq_

from douglas.plugins import pages
from douglas.tests import PluginTest


class PagesTest(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, pages)

    def test_is_frontpage(self):
        # test setup-related is_frontpage = False possibilities
        eq_(pages.is_frontpage({}, {}), False)
        eq_(pages.is_frontpage({'PATH_INFO': '/'}, {}), False)
        eq_(pages.is_frontpage({'PATH_INFO': '/'}, {'pages_frontpage': False}),
            False)

        # test path-related possibilities
        for path, expected in (('/', True),
                               ('/index', True),
                               ('/index.html', True),
                               ('/index.xml', True),
                               ('/foo', False)):
            eq_(pages.is_frontpage({'PATH_INFO': path},
                                   {'pages_frontpage': True}),
                expected)

    def test_pages(self):
        self.create_file('pages/about.txt', dedent("""\
        About this blog
        #meta1 val1
        body
        """))

        extra_cfg = {
            'pagesdir': os.path.join(self.datadir, 'pages')
        }
        req = self.build_request(extra_cfg)

        req.get_http()['PATH_INFO'] = '/pages/about'
        entries = pages.cb_filelist({'request': req})

        eq_(len(entries), 1)
        eq_(entries[0]['title'], 'About this blog')
