import os

from nose.tools import eq_

from douglas.plugins import tags
from douglas.tests import PluginTest


class TagsTest(PluginTest):
    def setUp(self):
        PluginTest.setUp(self, tags)

    def test_get_tagsfile(self):
        cfg = {"datadir": self.datadir}
        eq_(tags.get_tagsfile(cfg),
            os.path.join(self.datadir, os.pardir, "tags.index"))

        tags_filename = os.path.join(self.datadir, "tags.db")
        cfg = {"datadir": self.datadir, "tags_filename": tags_filename}
        eq_(tags.get_tagsfile(cfg), tags_filename)

    def test_functions(self):
        tm = tags.TagManager(self.request)
        tm._tagsdata = {
            'blog': ['firstpost.txt', 'secondpost.txt'],
            'legos': ['deathstar.txt'],
            'kids': ['omg2yearsold.txt'],
        }
        tm.all_tags()
        tm.all_tags_div()
        tm.all_tags_cloud()

        # self.entry has no tags metadata
        tm.entry_tags(self.entry)
        tm.entry_tags_span(self.entry)

        self.entry['tags'] = 'blog,kids'
        tm.entry_tags(self.entry)
        tm.entry_tags_span(self.entry)

    def test_tag_cloud_no_tags(self):
        tm = tags.TagManager(self.request)
        tm._tagsdata = {}
        eq_(tm.all_tags_cloud(),
            '<div class="allTagsCloud">\n</div>'
        )

    def test_tag_cloud_one_tag(self):
        tm = tags.TagManager(self.request)
        tm._tagsdata = {'tag2': ['a']}
        eq_(tm.all_tags_cloud(),
            '<div class="allTagsCloud">\n'
            '<a class="tag smallestTag" href="http://example.com/tag/tag2.html">tag2</a>\n'
            '</div>')

    def test_tag_cloud_many_tags(self):
        tm = tags.TagManager(self.request)
        tm._tagsdata = {
            "tag1": ["a", "b", "c", "d", "e", "f"],
            "tag2": ["a", "b", "c", "d"],
            "tag3": ["a"]
            }
        eq_(tm.all_tags_cloud(),
            '<div class="allTagsCloud">\n'
            '<a class="tag biggestTag" href="http://example.com/tag/tag1.html">tag1</a>\n'
            '<a class="tag mediumTag" href="http://example.com/tag/tag2.html">tag2</a>\n'
            '<a class="tag smallestTag" href="http://example.com/tag/tag3.html">tag3</a>\n'
            '</div>')
