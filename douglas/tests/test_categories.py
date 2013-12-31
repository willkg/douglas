import os

from nose.tools import eq_

from douglas.plugins import categories
from douglas.tests import PluginTest


def parse_text():
    return


class Test_categories(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, categories)
        # FIXME - should run initialize here instead
        self.request.get_configuration()['extensions'] = {'txt': parse_text}

    def tearDown(self):
        PluginTest.tearDown(self)

    def generate_entry(self, filename):
        filename = os.path.join(self.datadir, filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as fp:
            fp.write('Test entry at {0}\nbody body body\n'.format(filename))

    def test_no_categories(self):
        cm = categories.CategoryManager(self.request)
        eq_(cm.as_list(),
            '<ul class="categorygroup">\n\n</ul>')

    def test_categories(self):
        self.generate_entry('test1.txt')
        self.generate_entry('cat1/test_cat1.txt')
        self.generate_entry('cat2/test_cat2.txt')
        self.generate_entry('cat2/subcat2//test_sub1.txt')

        cm = categories.CategoryManager(self.request)
        eq_(cm.as_list(),
            '<ul class="categorygroup">\n'
            '<li><a href="http://example.com/index.html">/</a>(4)</li>\n'
            '<li><ul class="categorygroup">\n'
            '<li><a href="http://example.com/cat1/index.html">cat1/</a>(1)'
            '</li>\n'
            '<li><a href="http://example.com/cat2/index.html">cat2/</a>(2)'
            '</li>\n'
            '<li><ul class="categorygroup">\n'
            '<li><a href="http://example.com/cat2/subcat2/index.html">'
            'subcat2/</a>(1)</li>\n'
            '</ul></li>'
            '</ul></li>\n'
            '</ul>')
