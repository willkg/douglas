from douglas.app import blosxom_process_path_info
from douglas.tests import UnitTestBase


class Testpathinfo(UnitTestBase):
    """This tests default parsing of the path."""
    def _basic_test(self, pathinfo, expected, cfg=None, http=None, data=None):
        _http = {'PATH_INFO': pathinfo}
        if http:
            _http.update(http)
        req = self.build_request(cfg=cfg, http=_http, data=data)
        blosxom_process_path_info(args={'request': req})
        # print repr(expected), repr(req.data)
        self.dictsubset(expected, req.data)

    def test_root(self):
        self.setup_files(self.build_file_set([]))

        # /
        self._basic_test('/',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /index
        self._basic_test('/index',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /index.xml
        self._basic_test('/index.xml',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'xml'})

    def test_files(self):
        self.setup_files(self.build_file_set([
            'file1.txt', 'cata/file2.txt', 'catb/file3.txt']))

        # /file1
        self._basic_test('/file1',
                         {'bl_type': 'entry',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /cata/file2
        self._basic_test('/cata/file2',
                         {'bl_type': 'entry',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})

    def test_categories(self):
        self.setup_files(self.build_file_set([
            'cata/entry1.txt', 'cata/suba/entry1.txt', 'catb/entry1.txt']))

        # /cata
        self._basic_test('/cata',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /cata/
        self._basic_test('/cata/',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /cata/suba
        self._basic_test('/cata/suba',
                         {'bl_type': 'entry_list',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})
        # /cata/suba
        self._basic_test('/cata/suba/entry1.html',
                         {'bl_type': 'entry',
                          'pi_yr': '', 'pi_mo': '', 'pi_da': '',
                          'theme': 'html'})

    def test_dates_year(self):
        self._basic_test('/2012',
                         expected={
                             'bl_type': 'entry_list',
                             'pi_yr': '2012',
                             'pi_mo': '',
                             'pi_da': '',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': True
                         })

        self._basic_test('/2012',
                         expected={
                             'bl_type': '',
                             'pi_yr': '',
                             'pi_mo': '',
                             'pi_da': '',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': False
                         })

    def test_dates_month(self):
        self._basic_test('/2012/02',
                         expected={
                             'bl_type': 'entry_list',
                             'pi_yr': '2012',
                             'pi_mo': '02',
                             'pi_da': '',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': True,
                             'month_indexes': True
                         })

        self._basic_test('/2012/02',
                         expected={
                             'bl_type': '',
                             'pi_yr': '',
                             'pi_mo': '',
                             'pi_da': '',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': True,
                             'month_indexes': False
                         })

    def test_dates_day(self):
        self._basic_test('/2012/02/04',
                         expected={
                             'bl_type': 'entry_list',
                             'pi_yr': '2012',
                             'pi_mo': '02',
                             'pi_da': '04',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': True,
                             'month_indexes': True,
                             'day_indexes': True
                         })

        self._basic_test('/2012/02/04',
                         expected={
                             'bl_type': '',
                             'pi_yr': '',
                             'pi_mo': '',
                             'pi_da': '',
                             'theme': 'html'
                         },
                         cfg={
                             'year_indexes': True,
                             'month_indexes': True,
                             'day_indexes': False
                         })

    def test_theme(self):
        # The theme is the default theme, the extension of the request,
        # or the theme= querystring.
        self.setup_files(self.build_file_set([
            '2007/entry1.txt', '2007/05/entry3.txt', 'cata/entry2.txt']))

        self._basic_test('/', {'theme': 'html'})
        self._basic_test('/index.xml', {'theme': 'xml'})
        self._basic_test('/cata/index.foo', {'theme': 'foo'})

        # FIXME - need a test for querystring
        # self._basic_test( '/cata/index.foo', http={ 'QUERY_STRING':
        # 'theme=bar' },
        #                   expected={ 'theme': 'bar' } )

        # test that we pick up the default_theme config variable
        self._basic_test('/', cfg={'default_theme': 'foo'},
                         expected={'theme': 'foo'})

        # FIXME - need tests for precedence of theme indicators

    def test_url(self):
        # The url is the HTTP PATH_INFO env variable.
        self.setup_files(self.build_file_set([
            '2007/entry1.txt', '2007/05/entry3.txt', 'cata/entry2.txt']))

        self._basic_test('/', {'url': 'http://www.example.com/'})
        self._basic_test('/index.xml',
                         {'url': 'http://www.example.com/index.xml'})
        self._basic_test('/cata/index.foo',
                         {'url': 'http://www.example.com/cata/index.foo'})

    def test_pi_bl(self):
        # pi_bl is the entry the user requested to see if the request indicated
        # a specific entry.  It's the empty string otherwise.
        self.setup_files(self.build_file_set([
            '2007/entry1.txt', '2007/05/entry3.txt', 'cata/entry2.txt']))

        self._basic_test('', {'pi_bl': ''})
        self._basic_test('/', {'pi_bl': '/'})
        self._basic_test('/index.xml', {'pi_bl': '/index.xml'})
        self._basic_test('/2007/index.xml', {'pi_bl': '/2007/index.xml'})
        self._basic_test('/cata/entry2', {'pi_bl': '/cata/entry2'})
