"""
This module contains the base class for all the Entry classes.  The
EntryBase class is essentially the API for entries in douglas.  Reading
through the comments for this class will walk you through building your
own EntryBase derivatives.

This module also holds a generic generate_entry function which will generate
a BaseEntry with data that you provide for it.
"""

import locale
import time
from UserDict import DictMixin


BIGNUM = 2000000000


class EntryBase(object, DictMixin):
    """
    EntryBase is the base class for all the Entry classes.  Each
    instance of an Entry class represents a single entry in the
    weblog, whether it came from a file, or a database, or even
    somewhere off the InterWeeb.

    EntryBase derivatives are dict-like.
    """
    def __init__(self, request):
        self._metadata = dict()
        self._id = ''
        self._mtime = BIGNUM
        self._request = request

    def __repr__(self):
        """
        Returns a friendly debuggable representation of self. Useful
        to know on what entry douglas fails on you (though unlikely)

        :returns: Identifiable representation of object
        """
        return "<Entry instance: %s>\n" % self.get_id()

    def get_id(self):
        """
        This should return an id that's unique enough for caching
        purposes.

        Override this.

        :returns: string id
        """
        return self._id

    def set_time(self, timetuple):
        """
        This takes in a given time tuple and sets all the magic
        metadata variables we have according to the items in the time
        tuple.

        :param timetuple: the timetuple to use to set the data
                          with--this is the same thing as the
                          mtime/atime portions of an os.stat.  This
                          time is expected to be local time, not UTC.
        """
        self._mtime = time.mktime(timetuple)
        gmtimetuple = time.gmtime(self._mtime)

        self._metadata.update({
            'timetuple': timetuple,
            'mtime': self._mtime,
            'ti': time.strftime('%H:%M', timetuple),
            'mo': time.strftime('%b', timetuple),
            'mo_num': time.strftime('%m', timetuple),
            'da': time.strftime('%d', timetuple),
            'dw': time.strftime('%A', timetuple),
            'yr': time.strftime('%Y', timetuple),
            'fulltime': time.strftime('%Y%m%d%H%M%S', timetuple),
            'date': time.strftime('%a, %d %b %Y', timetuple)
        })

        # YYYY-MM-DDThh:mm:ssZ
        self._metadata['w3cdate'] = time.strftime(
            '%Y-%m-%dT%H:%M:%SZ', gmtimetuple)

        # Temporarily disable the set locale, so RFC-compliant date is
        # really RFC-compliant: directives %a and %b are locale
        # dependent.  Technically, we're after english locale, but
        # only 'C' locale is guaranteed to exist.
        loc = locale.getlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, 'C')

        self._metadata['rfc822date'] = time.strftime(
            '%a, %d %b %Y %H:%M GMT', gmtimetuple)

        # set the locale back
        locale.setlocale(locale.LC_ALL, loc)

    # Everything below this point implements the bits required for the
    # DictMixin.

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        for key in self.keys():
            yield key

    def __delitem__(self, key):
        return self._metadata.__delitem__(key)

    def __getitem__(self, key):
        return self._metadata.__getitem__(key)

    def __setitem__(self, key, value):
        return self._metadata.__setitem__(key, value)

    def keys(self):
        return self._metadata.keys()


def generate_entry(request, properties, data, mtime=None):
    """
    Takes a properties dict and a data string and generates a generic
    entry using the data you provided.

    :param request: the Request object

    :param properties: the dict of properties for the entry

    :param data: the data content for the entry

    :param mtime: the mtime tuple (as given by ``time.localtime()``).
                  if you pass in None, then we'll use localtime.
    """
    entry = EntryBase(request)

    entry.update(properties)
    entry['body'] = data
    if mtime:
        entry.set_time(mtime)
    else:
        entry.set_time(time.localtime())
    return entry
