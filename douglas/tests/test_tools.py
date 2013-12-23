# -*- coding: utf-8 -*-
import os
import os.path
import string
from textwrap import dedent

from nose.tools import eq_

from douglas import app, tools
from douglas.tests import UnitTestBase


req = app.Request({}, {}, {})


class Testparse_entry_file(UnitTestBase):
    def test_empty(self):
        fn = self.create_file('test1.txt', '')
        data = tools.parse_entry_file(fn)
        eq_(data, {'body': '', 'title': ''})

    def test_title(self):
        fn = self.create_file('test1.txt', 'Only a title')
        data = tools.parse_entry_file(fn)
        eq_(data, {'body': '', 'title': 'Only a title'})

    def test_title_body(self):
        fn = self.create_file('test1.txt', 'Only a title\nbody')
        data = tools.parse_entry_file(fn)
        eq_(data, {'body': 'body', 'title': 'Only a title'})

    def test_metadata(self):
        fn = self.create_file('test1.txt', dedent("""\
        Only a title
        #meta1
        #meta2 val2
        #meta3  val3
        #meta4   """ + """
        Body
        Body
        Body
        """))
        data = tools.parse_entry_file(fn)
        eq_(data,
            {'title': 'Only a title', 'body': 'Body\nBody\nBody\n',
             'meta1': '1', 'meta2': 'val2', 'meta3': 'val3', 'meta4': '1'})


class Testescape_text(UnitTestBase):
    """tools.escape_text"""
    def test_none_to_none(self):
        eq_(tools.escape_text(None), None)

    def test_empty_string_to_empty_string(self):
        eq_(tools.escape_text(''), '')

    def test_single_quote_to_pos(self):
        eq_(tools.escape_text('a\'b'), 'a&#x27;b')

    def test_double_quote_to_quot(self):
        eq_(tools.escape_text('a"b'), 'a&quot;b')

    def test_greater_than(self):
        eq_(tools.escape_text('a>b'), 'a&gt;b')

    def test_lesser_than(self):
        eq_(tools.escape_text('a<b'), 'a&lt;b')

    def test_ampersand(self):
        eq_(tools.escape_text('a&b'), 'a&amp;b')

    def test_complicated_case(self):
        eq_(tools.escape_text('a&>b'), 'a&amp;&gt;b')

    def test_everything_else_unchanged(self):
        for mem in ((None, None),
                    ('', ''),
                    ('abc', 'abc')):
            eq_(tools.escape_text(mem[0]), mem[1])


class Testurlencode_text(UnitTestBase):
    """tools.urlencode_text"""
    def test_none_to_none(self):
        eq_(tools.urlencode_text(None), None)

    def test_empty_string_to_empty_string(self):
        eq_(tools.urlencode_text(''), '')

    def test_equals_to_3D(self):
        eq_(tools.urlencode_text('a=c'), 'a%3Dc')

    def test_ampersand_to_26(self):
        eq_(tools.urlencode_text('a&c'), 'a%26c')

    def test_space_to_20(self):
        eq_(tools.urlencode_text('a c'), 'a%20c')

    def test_utf8(self):
        eq_(tools.urlencode_text('español'), 'espa%C3%B1ol')

    def test_everything_else_unchanged(self):
        for mem in ((None, None),
                    ('', ''),
                    ('abc', 'abc')):
            eq_(tools.urlencode_text(mem[0]), mem[1])


class Testimportname(UnitTestBase):
    """tools.importname"""
    def setUp(self):
        UnitTestBase.setUp(self)
        tools._config = {}

    def tearDown(self):
        UnitTestBase.tearDown(self)
        if '_config' in tools.__dict__:
            del tools.__dict__['_config']

    def _c(self, mn, n):
        m = tools.importname(mn, n)
        # print repr(m)
        return m

    def test_goodimport(self):
        eq_(tools.importname('', 'string'), string)
        eq_(tools.importname('os', 'path'), os.path)

    def test_badimport(self):
        eq_(tools.importname('', 'foo'), None)


class Testwhat_ext(UnitTestBase):
    """tools.what_ext"""
    def get_ext_dir(self):
        return os.path.join(self.datadir, 'ext')

    def setUp(self):
        """
        Creates the directory with some files in it.
        """
        UnitTestBase.setUp(self)
        self._files = ['a.txt', 'b.html', 'c.txtl', 'español.txt']
        os.mkdir(self.get_ext_dir())

        for mem in self._files:
            with open(os.path.join(self.get_ext_dir(), mem), 'w') as fp:
                fp.write('lorem ipsum')

    def test_returns_extension_if_file_has_extension(self):
        d = self.get_ext_dir()
        eq_(tools.what_ext(['txt', 'html'], os.path.join(d, 'a')), 'txt')
        eq_(tools.what_ext(['txt', 'html'], os.path.join(d, 'b')), 'html')
        eq_(tools.what_ext(['txt', 'html'], os.path.join(d, 'español')), 'txt')

    def test_returns_None_if_extension_not_present(self):
        d = self.get_ext_dir()
        eq_(tools.what_ext([], os.path.join(d, 'a')), None)
        eq_(tools.what_ext(['html'], os.path.join(d, 'a')), None)


class Testconvert_configini_values(UnitTestBase):
    """tools.convert_configini_values

    This tests config.ini -> config conversions.
    """
    def test_empty(self):
        eq_(tools.convert_configini_values({}), {})

    def test_no_markup(self):
        eq_(tools.convert_configini_values({'a': 'b'}), {'a': 'b'})

    def test_integers(self):
        for mem in (({'a': '1'}, {'a': 1}),
                    ({'a': '1', 'b': '2'}, {'a': 1, 'b': 2}),
                    ({'a': '10'}, {'a': 10}),
                    ({'a': '100'}, {'a': 100}),
                    ({'a': ' 100  '}, {'a': 100})):
            eq_(tools.convert_configini_values(mem[0]), mem[1])

    def test_strings(self):
        for mem in (({'a': '\'b\''}, {'a': 'b'}),
                    ({'a': '\"b\"'}, {'a': 'b'}),
                    ({'a': '   \"b\" '}, {'a': 'b'}),
                    ({'a': 'español'}, {'a': 'español'}),
                    ({'a': '\'español\''}, {'a': 'español'})):
            eq_(tools.convert_configini_values(mem[0]), mem[1])

    def test_lists(self):
        for mem in (({'a': '[]'}, {'a': []}),
                    ({'a': '[1]'}, {'a': [1]}),
                    ({'a': '[1, 2]'}, {'a': [1, 2]}),
                    ({'a': '  [1 ,2 , 3]'}, {'a': [1, 2, 3]}),
                    ({'a': '[\'1\' ,\"2\" , 3]'}, {'a': ['1', '2', 3]})):
            eq_(tools.convert_configini_values(mem[0]), mem[1])

    def test_syntax_exceptions(self):
        for mem in ({'a': '\'b'},
                    {'a': 'b\''},
                    {'a': '"b'},
                    {'a': 'b"'},
                    {'a': '[b'},
                    {'a': 'b]'}):
            self.assertRaises(tools.ConfigSyntaxErrorException,
                              tools.convert_configini_values, mem)


class Testurl_rewrite(UnitTestBase):
    def test_basic(self):
        eq_(tools.url_rewrite('', '', ''), '')
        eq_(tools.url_rewrite(
            '<a href="/">blah</a>',
            '/',
            'http://localhost:8000/'),
            '<a href="http://localhost:8000/">blah</a>')
        eq_(tools.url_rewrite(
            '<img src="/foo.gif">',
            '/',
            'http://localhost:8000/'),
            '<img src="http://localhost:8000/foo.gif">')
