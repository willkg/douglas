from douglas.app import Request
from douglas.plugins import readmore
from douglas.tests import PluginTest


class ReadmoreTest(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, readmore)

    def test_story_no_break(self):
        req = Request({"base_url": "/"}, {}, {"bl_type": "file"})

        args = {"entry": {"body": "no break",
                          "file_path": ""},
                "request": req}

        readmore.cb_story(args)
        self.assertEquals(args["entry"]["body"], "no break")

    def test_story_break_single_file(self):
        # if showing a single file, then we nix the BREAK bit.
        req = Request({"base_url": "/"}, {}, {"bl_type": "file"})

        args = {"entry": {"body": "no BREAK break",
                          "file_path": ""},
                "request": req}

        readmore.cb_story(args)
        self.assertEquals(args["entry"]["body"], "no  break")

    def test_story_break_index(self):
        # if showing the entry in an index, then we replace the BREAK
        # with the template and nix everything after BREAK.
        req = Request({"readmore_template": "FOO", "base_url": "/"},
                      {},
                      {"bl_type": "dir"})

        args = {"entry": {"body": "no BREAK break",
                          "file_path": ""},
                "request": req}

        readmore.cb_story(args)
        self.assertEquals(args["entry"]["body"], "no FOO")

    # FIXME: write test for cb_start -- requires docutils or
    # mocking framework
