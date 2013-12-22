from douglas.tests import PluginTest
from douglas.plugins import yeararchives


class Test_yeararchives(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, yeararchives)

    def tearDown(self):
        PluginTest.tearDown(self)

    def test_parse_path_info(self):
        testdata = [
            ("", None),
            ("/", None),
            ("/2003", ("2003", None)),
            ("/2003/", ("2003", None)),
            ("/2003/index", ("2003", None)),
            ("/2003/index.theme", ("2003", "theme")),
        ]

        for testin, testout in testdata:
            self.assertEquals(yeararchives.parse_path_info(testin),
                              testout)
