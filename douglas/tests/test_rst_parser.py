import os
from textwrap import dedent

from nose.tools import eq_

from douglas.plugins import rst_parser
from douglas.tests import PluginTest


class TagsTest(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, rst_parser)

    def create_file(self, fn, data):
        os.makedirs(os.path.join(self.datadir, 'entries'))
        fn = os.path.join(self.datadir, 'entries', fn)
        with open(fn, 'w') as fp:
            fp.write(data)

        return fn

    def test_parsing(self):
        fn = self.create_file('blogpost.rst', dedent("""\
        The Title
        #meta1 val1
        This is my blog post
        ====================

        **so amazing**
        """))
        ret = rst_parser.parse_rst_file(fn, self.request)
        eq_(ret,
            {'title': 'The Title',
             'body': ('<div class="section" id="this-is-my-blog-post">\n'
                      '<h1>This is my blog post</h1>\n'
                      '<p><strong>so amazing</strong></p>\n'
                      '</div>\n'),
             'meta1': 'val1'})

    def test_break(self):
        fn = self.create_file('blogpost.rst', dedent("""\
        The Title
        #meta1 val1
        first part

        .. break::

        second part
        """))
        ret = rst_parser.parse_rst_file(fn, self.request)
        eq_(ret,
            {'title': 'The Title',
             'summary': '<p>first part</p>\n',
             'body': '<p>first part</p>\n<p>second part</p>\n',
             'meta1': 'val1'})
