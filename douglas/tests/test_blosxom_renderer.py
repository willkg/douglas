from StringIO import StringIO

from nose.tools import eq_

from douglas.app import Request
from douglas.renderers import blosxom
from douglas.tests import UnitTestBase

req = Request({}, {}, {})


class TestBlosxomRenderer(UnitTestBase):
    def test_dollar_parse_problem(self):
        output = StringIO()
        renderer = blosxom.BlosxomRenderer(req, output)
        renderer.theme = {"story": "$(body)"}

        # mocking out _run_callback to just return the args dict
        renderer._run_callback = lambda c, args: args

        entry = {"body": r'PS1="\u@\h \[\$foo \]\W\[$RST\] \$"'}

        # the rendered template should be exactly the same as the body
        # in the entry--no \$ -> $ silliness.
        eq_(renderer.render_template(entry, "story"),
            entry["body"])

    def test_date_head(self):
        output = StringIO()
        renderer = blosxom.BlosxomRenderer(req, output)
        renderer.theme = {"date_head": "$(yr) $(mo) $(da) $(date)"}

        # mocking out _run_callback to just return the args dict
        renderer._run_callback = lambda c, args: args

        vardict = {
            "yr": "2011",
            "mo": "01",
            "da": "25",
            "date": "Tue, 25 Jan 2011"
            }

        eq_(renderer.render_template(vardict, "date_head"),
            "2011 01 25 Tue, 25 Jan 2011")
