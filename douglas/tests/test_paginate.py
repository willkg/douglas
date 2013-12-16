from nose.tools import eq_

from douglas.plugins import paginate
from douglas.tests import PluginTest


class PaginateTest(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, paginate)

    def test_functions(self):
        entry_list = self.generate_entry_list(self.request, 50)
        self.request._data['entry_list'] = entry_list
        self.request._data['bl_type'] = 'entry_list'

        paginate.cb_truncatelist({
            'request': self.request,
            'entry_list': self.request.get_data()['entry_list']
        })

        new_entry_list = self.request.get_data()['entry_list']
        pager = self.request.get_data()['pager']

        eq_(len(new_entry_list), 10)
        eq_(pager.number, 1)
        eq_(pager.has_next(), True)
        eq_(pager.has_previous(), False)
        pager.as_list()
        pager.as_span()
