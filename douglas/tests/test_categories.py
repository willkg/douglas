import os

from douglas.plugins import categories
from douglas.tests import PluginTest


def parse_text():
    return


class Test_categories(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, categories)
        # FIXME - should run initialize here instead
        self.request.get_configuration()["extensions"] = {"txt": parse_text}

    def tearDown(self):
        PluginTest.tearDown(self)

    def test_cb_prepare(self):
        self.assert_("categorylinks" not in self.request.get_data())
        categories.cb_prepare(self.args)
        self.assert_("categorylinks" in self.request.get_data())

    def test_verify_installation(self):
        self.assert_(categories.verify_installation)

    def test_no_categories(self):
        categories.cb_prepare(self.args)
        self.assertEquals(
            str(self.request.get_data()["categorylinks"]),
            "<ul class=\"categorygroup\">\n\n</ul>")

    def generate_entry(self, filename):
        filename = os.path.join(self.datadir, filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            
        file = open(filename, "w")
        file.write("Test entry at %s\nbody body body\n" % filename)
        file.close()

    def test_categories(self):
        self.generate_entry("test1.txt")
        self.generate_entry("cat1/test_cat1.txt")
        self.generate_entry("cat2/test_cat2.txt")

        categories.cb_prepare(self.args)
        self.assertEquals(
            str(self.request.get_data()["categorylinks"]),
            "\n".join(
                ['<ul class="categorygroup">',
                 '<li><a href="http://example.com//index.html">/</a> (3)</li>',
                 '<li><ul class="categorygroup">',
                 '<li><a href="http://example.com//cat1/index.html">cat1/</a> (1)</li>',
                 '<li><a href="http://example.com//cat2/index.html">cat2/</a> (1)</li>',
                 '</ul></li>',
                 '</ul>']))
