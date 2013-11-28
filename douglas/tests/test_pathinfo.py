from douglas import tools
from douglas.app import blosxom_process_path_info
from douglas.tests import UnitTestBase


class Testpathinfo(UnitTestBase):
    """This tests default parsing of the path."""
    def _basic_test(self, pathinfo, expected, cfg=None, http=None, data=None):
        _http = {"PATH_INFO": pathinfo}
        if http:
            _http.update(http)
        req = self.build_request(cfg=cfg, http=_http, data=data)
        blosxom_process_path_info(args={"request": req})
        # print repr(expected), repr(req.data)
        self.cmpdict(expected, req.data)
 
    def test_root(self):
        entries = self.build_file_set([])

        self.setup_files(entries)
        try:
            # /
            self._basic_test("/",
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /index
            self._basic_test("/index", 
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /index.xml
            self._basic_test("/index.xml", 
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "xml"})
        finally:
            self.tearDown()

    def test_files(self):
        entries = self.build_file_set(["file1.txt",
                                       "cata/file2.txt",
                                       "catb/file3.txt"])

        self.setup_files(entries)
        try:
            # /file1
            self._basic_test("/file1",
                             {"bl_type": "entry",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /cata/file2
            self._basic_test("/cata/file2",
                             {"bl_type": "entry",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
        finally:
            self.tearDown()

    def test_categories(self):
        entries = self.build_file_set(["cata/entry1.txt",
                                       "cata/suba/entry1.txt",
                                       "catb/entry1.txt"])

        self.setup_files(entries)
        try:
            # /cata
            self._basic_test("/cata", 
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /cata/
            self._basic_test("/cata/", 
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /cata/suba
            self._basic_test("/cata/suba", 
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /cata/suba
            self._basic_test("/cata/suba/entry1.html", 
                             {"bl_type": "entry",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
        finally:
            self.tearDown()

    def test_dates(self):
        tools.initialize()

        self._basic_test("/2002",
                         {"bl_type": "entry_list",
                          "pi_yr": "2002", "pi_mo": "", "pi_da": "",
                          "theme": "html"})
        self._basic_test("/2002/02",
                         {"bl_type": "entry_list",
                          "pi_yr": "2002", "pi_mo": "02", "pi_da": "",
                          "theme": "html"})
        self._basic_test("/2002/02/04", 
                         {"bl_type": "entry_list",
                          "pi_yr": "2002", "pi_mo": "02", "pi_da": "04",
                          "theme": "html"})

    def test_categories_and_dates(self):
        tools.initialize()

        entries = self.build_file_set(["cata/entry1.txt",
                                       "cata/suba/entry1.txt",
                                       "catb/entry1.txt"])

        self.setup_files(entries)
        try:
            # /2006/cata/
            self._basic_test("/2006/cata/", 
                             {"bl_type": "entry_list",
                              "pi_yr": "2006", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /2006/04/cata/
            self._basic_test("/2006/04/cata/", 
                             {"bl_type": "entry_list",
                              "pi_yr": "2006", "pi_mo": "04", "pi_da": "",
                              "theme": "html"})
            # /2006/04/02/cata/
            self._basic_test("/2006/04/02/cata/", 
                             {"bl_type": "entry_list",
                              "pi_yr": "2006", "pi_mo": "04", "pi_da": "02",
                              "theme": "html"})
            # /2006/04/02/cata/suba/
            self._basic_test("/2006/04/02/cata/suba/", 
                             {"bl_type": "entry_list",
                              "pi_yr": "2006", "pi_mo": "04", "pi_da": "02",
                              "theme": "html"})

        finally:
            self.tearDown()

    def test_date_categories(self):
        entries = self.build_file_set(["2007/entry1.txt",
                                       "2007/05/entry3.txt",
                                       "cata/entry2.txt"])

        self.setup_files(entries)
        try:
            # /2007/              2007 here is a category
            self._basic_test("/2007/",
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /2007/05            2007/05 here is a category
            self._basic_test("/2007/05",
                             {"bl_type": "entry_list",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})
            # /2007/05/entry3     2007/05/entry3 is a file
            self._basic_test("/2007/05/entry3.html",
                             {"bl_type": "entry",
                              "pi_yr": "", "pi_mo": "", "pi_da": "",
                              "theme": "html"})

        finally:
            self.tearDown()

    def test_theme(self):
        # theme var tests
        # The theme is the default theme, the extension of the request,
        # or the theme= querystring.
        root = self.get_temp_dir()

        entries = self.build_file_set(["2007/entry1.txt", 
                                       "2007/05/entry3.txt", 
                                       "cata/entry2.txt"])

        self.setup_files(entries)

        try:
            self._basic_test("/", {"theme": "html"})
            self._basic_test("/index.xml", {"theme": "xml"})
            self._basic_test("/cata/index.foo", {"theme": "foo"})

            # FIXME - need a test for querystring
            # self._basic_test( "/cata/index.foo", http={ "QUERY_STRING": "theme=bar" },
            #                   expected={ "theme": "bar" } )

            # test that we pick up the default_theme config variable
            self._basic_test("/", cfg={"default_theme": "foo"},
                             expected={"theme": "foo"})

            # FIXME - need tests for precedence of theme indicators

        finally:
            self.tearDown()

    def test_url(self):
        # url var tests
        # The url is the HTTP PATH_INFO env variable.
        entries = self.build_file_set(["2007/entry1.txt", 
                                       "2007/05/entry3.txt", 
                                       "cata/entry2.txt"])

        self.setup_files(entries)

        try:
            self._basic_test("/", {"url": "http://www.example.com/"})
            self._basic_test("/index.xml", {"url": "http://www.example.com/index.xml"})
            self._basic_test("/cata/index.foo", {"url": "http://www.example.com/cata/index.foo"})

        finally:
            self.tearDown()

    def test_pi_bl(self):
        # pi_bl var tests
        # pi_bl is the entry the user requested to see if the request indicated
        # a specific entry.  It's the empty string otherwise.
        entries = self.build_file_set(["2007/entry1.txt", 
                                       "2007/05/entry3.txt", 
                                       "cata/entry2.txt"]) 

        self.setup_files(entries)

        try:
            self._basic_test("", {"pi_bl": ""})
            self._basic_test("/", {"pi_bl": "/"})
            self._basic_test("/index.xml", {"pi_bl": "/index.xml"})
            self._basic_test("/2007/index.xml", {"pi_bl": "/2007/index.xml"})
            self._basic_test("/cata/entry2", {"pi_bl": "/cata/entry2"})

        finally:
            self.tearDown()
