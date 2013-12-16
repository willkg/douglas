import os

from douglas.app import blosxom_entry_parser
from douglas.tests import UnitTestBase


class Testentryparser(UnitTestBase):
    """This tests parsing entry files"""
    def _basic_test(self, req, filedata, output_dict):
        datadir = req.get_configuration()["datadir"]
        if not os.path.exists(datadir):
            os.makedirs(datadir)

        filename = os.path.join(datadir, "firstpost.txt")

        with open(filename, 'w') as fp:
            fp.write(filedata)

        entry_dict = blosxom_entry_parser(filename, req)

        self.cmpdict(output_dict, entry_dict)

    def test_basic_entry(self):
        req = self.build_request()
        entry = ("First post!\n"
                 "<p>\n"
                 "First post!\n"
                 "</p>")

        self._basic_test(
            req, entry,
            {"title": "First post!", "body": "<p>\nFirst post!\n</p>"})

    def test_meta_data(self):
        req = self.build_request()
        entry = ("First post!\n"
                 "#music the doors\n"
                 "#mood happy\n"
                 "<p>\n"
                 "First post!\n"
                 "</p>")

        self._basic_test(
            req, entry,
            {"title": "First post!",
             "mood": "happy",
             "music": "the doors",
             "body": "<p>\nFirst post!\n</p>"})

    def test_meta_no_value(self):
        req = self.build_request()
        entry = ("First post!\n"
                 "#foo\n"
                 "<p>\n"
                 "First post!\n"
                 "</p>")

        self._basic_test(
            req, entry,
            {"title": "First post!", "foo": "1",
             "body": "<p>\nFirst post!\n</p>"})
