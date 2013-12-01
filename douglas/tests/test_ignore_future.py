import os
import time

from nose.tools import eq_

from douglas.app import initialize
from douglas.plugins import ignore_future
from douglas.tests import PluginTest
from douglas.tools import get_entries


class Test_ignore_future(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, ignore_future)
        self.config['load_plugins'] = ['douglas.plugins.ignore_future']
        initialize(self.config)

    def tearDown(self):
        PluginTest.tearDown(self)

    def generate_entry(self, filename, mtime):
        filename = os.path.join(self.datadir, filename)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
         
        with open(filename, 'w') as fp:
            fp.write('Test entry at {0}\nbody body body\n'.format(filename))

        os.utime(filename, (mtime, mtime))

    def test_fine(self):
        yesterday = time.time() - (60 * 60 * 24)

        self.generate_entry('test1.txt', yesterday)
        self.generate_entry('ignore1/test_ignore1.txt', yesterday)
        self.generate_entry('ignore2/test_ignore2.txt', yesterday)

        entries = get_entries(self.config, self.datadir)

        eq_(len(entries), 3)

    def test_future(self):
        tomorrow = time.time() + (60 * 60 * 24)
        yesterday = time.time() - (60 * 60 * 24)

        self.generate_entry('test1.txt', yesterday)
        self.generate_entry('ignore1/test_ignore1.txt', yesterday)
        self.generate_entry('ignore2/test_ignore2.txt', tomorrow)

        entries = get_entries(self.config, self.datadir)

        eq_(len(entries), 2)
