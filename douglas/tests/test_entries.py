import time
from os import environ

from nose.tools import eq_

from douglas.entries.base import EntryBase, generate_entry
from douglas.tests import req_, UnitTestBase
from douglas.tools import STANDARD_FILTERS


TIME1 = (2008, 7, 21, 12, 51, 47, 0, 203, 1)


class TestEntryBase(UnitTestBase):
    def test_data(self):
        e = EntryBase(req_())
        eq_(e.get_data(), "")

        s1 = "la la la la la"
        e.set_data(s1)
        eq_(e.get_data(), s1)
        eq_(type(e.get_data()), str)

        s2 = u"foo foo foo foo foo"
        e.set_data(s2)
        eq_(e.get_data(), s2)
        eq_(type(e.get_data()), str)

        s3 = "foo bar"
        e.set_data(s3)
        eq_(e.get_data(), s3)

    def test_metadata(self):
        e = EntryBase(req_())
        eq_(e.get_metadata_keys(), STANDARD_FILTERS.keys())
        eq_(e.get_metadata("foo"), None)
        eq_(e.get_metadata("foo", "bar"), "bar")
        e.set_metadata("foo", "bar")
        eq_(e.get_metadata("foo"), "bar")

    def test_time(self):
        e = EntryBase(req_())
        # set_time takes local time, and results depend on time zone.
        self.__force_tz()
        e.set_time(TIME1)
        self.__restore_tz()
        for mem in (("timetuple", TIME1),
                    ("mtime", 1216659107.0),
                    ("ti", "12:51"),
                    ("mo", "Jul"),
                    ("mo_num", "07"),
                    ("da", "21"),
                    ("dw", "Monday"),
                    ("yr", "2008"),
                    ("fulltime", "20080721125147"),
                    ("date", "Mon, 21 Jul 2008"),
                    ("w3cdate", "2008-07-21T16:51:47Z"),
                    ("rfc822date", "Mon, 21 Jul 2008 16:51 GMT")):
            eq_(e[mem[0]], mem[1], \
                  "%s != %s (note: this is a time zone dependent test)" % (mem[0], mem[1]))

    def test_dictlike(self):
        e = EntryBase(req_())
        e["foo"] = "bar"
        e["body"] = "entry body"

        def sortlist(l):
            l.sort()
            return l

        eq_(sortlist(e.keys()), sortlist(STANDARD_FILTERS.keys() + ["foo", "body"]))

        eq_(e["foo"], "bar")
        eq_(e.get("foo"), "bar")
        eq_(e.get("foo", "fickle"), "bar")
        eq_(e.get_metadata("foo"), "bar")
        eq_(e.get_metadata("foo", "fickle"), "bar")

        eq_(e["body"], "entry body", "e[\"body\"]")
        eq_(e.get("body"), "entry body", "e.get(\"body\")")
        eq_(e.get_data(), "entry body", "e.getData()")

        eq_(e.get("missing_key", "default"), "default")
        eq_(e.get("missing_key"), None)

        # e.set("faz", "baz")
        # yield eq_, e.get("faz"), "baz"

        eq_(e.has_key("foo"), True)
        eq_(e.has_key("foo2"), False)
        eq_(e.has_key("body"), True)

        # FIXME - EntryBase doesn't support "in" operator.
        # eq_("foo" in e, True)
        # eq_("foo2" in e, False)
        # eq_("foo2" not in e, True)
        # eq_("body" in e, True)

        e.update({"foo": "bah", "faux": "pearls"})
        eq_(e["foo"], "bah")
        eq_(e["faux"], "pearls")

        e.update({"body": "new body data"})
        eq_(e["body"], "new body data")
        eq_(e.get_data(), "new body data")

        # del e["foo"]
        # yield eq_, e.get("foo"), None

    # @raises(KeyError)
    # def test_delitem_keyerror(self):
    #     e = EntryBase(req_())
    #     del e["missing_key"]

    # @raises(ValueError)
    # def test_delitem_valueerror(self):
    #     e = EntryBase(req_())
    #     del e["body"]

    def test_generate_entry(self):
        # generate_entry takes local time, and we test the resulting
        # rfc822date which is UTC.  Result depends on time zone.
        self.__force_tz()
        e = generate_entry(req_(), {"foo": "bar"}, "entry body", TIME1)
        self.__restore_tz()

        eq_(e["foo"], "bar")
        eq_(e["body"], "entry body")
        eq_(e["rfc822date"], "Mon, 21 Jul 2008 16:51 GMT")

        e = generate_entry(req_(), {"foo": "bar"}, "entry body")

    def test_repr(self):
        # it doesn't really matter what __repr__ sends back--it's only used
        # for logging/debugging.  so this test adds coverage for that line to
        # make sure it doesn't error out.
        e = EntryBase(req_())
        repr(e)

    def __force_tz(self):
        """
        Force time zone to 'US/Eastern'.

        Some of the above tests are time zone dependent.
        """
        self.__tz = environ.get('TZ')
        environ['TZ'] = 'US/Eastern'
        time.tzset()
    
    def __restore_tz(self):
        """
        Restore time zone to what it was before __force_tz() call.
        """
        if self.__tz:
            environ['TZ'] = self.__tz
            self.__tz = None
        else:
            del environ['TZ']
        time.tzset()
