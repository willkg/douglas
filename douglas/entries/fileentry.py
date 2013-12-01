import os
import re
import time

from douglas import tools
from douglas.entries import base


class FileEntry(base.EntryBase):
    """
    This class gets it's data and metadata from the file specified
    by the filename argument.
    """
    def __init__(self, request, filename, root, datadir=""):
        """
        :arg request: the Request object
        :arg filename: the complete filename for the file in question
            including path
        :arg root: i have no clue what this is
        :arg datadir: the datadir
        """
        base.EntryBase.__init__(self, request)
        self._config = request.get_configuration()
        self._filename = filename.replace(os.sep, '/')
        self._root = root.replace(os.sep, '/')

        self._datadir = datadir or self._config["datadir"]
        if self._datadir.endswith(os.sep):
            self._datadir = self._datadir[:-1]

        self._timetuple = tools.filestat(self._request, self._filename)
        self._mtime = time.mktime(self._timetuple)
        self._fulltime = time.strftime("%Y%m%d%H%M%S", self._timetuple)
        self.__populated = 0

    def __repr__(self):
        return "<fileentry f'%s' r'%s'>" % (self._filename, self._root)

    def get_id(self):
        """
        Returns the id for this content item--in this case, it's the
        filename.

        :returns: the id of the fileentry (the filename)
        """
        return self._filename

    def keys(self):
        if not self.__populated:
            self._populatedata()
        return super(FileEntry, self).keys()

    def __delitem__(self, key):
        if not self.__populated:
            self._populatedata()
        return super(FileEntry, self).__delitem__(key)

    def __getitem__(self, key):
        if not self.__populated:
            self._populatedata()
        return super(FileEntry, self).__getitem__(key)

    def __setitem__(self, key, value):
        if not self.__populated:
            self._populatedata()
        return super(FileEntry, self).__setitem__(key, value)

    def _populatedata(self):
        """
        Fills the metadata dict with metadata about the given file.
        This metadata consists of things we pick up from an os.stat
        call as well as knowledge of the filename and the root
        directory.  We then parse the file and fill in the rest of the
        information that we know.
        """
        file_basename = os.path.basename(self._filename)

        # FIXME - this code is crazy
        path = self._filename.replace(self._root, '')
        path = path.replace(os.path.basename(self._filename), '')
        path = path[:-1]

        absolute_path = self._filename.replace(self._datadir, '')
        absolute_path = self._filename.replace(self._datadir, '', 1)
        absolute_path = absolute_path.replace(file_basename, '')
        absolute_path = absolute_path[1:][:-1]

        if absolute_path and absolute_path[-1] == "/":
            absolute_path = absolute_path[0:-1]

        filenamenoext = os.path.splitext(file_basename)[0]
        if absolute_path == '':
            file_path = filenamenoext
        else:
            file_path = '/'.join((absolute_path, filenamenoext))

        tb_id = '%s/%s' % (absolute_path, filenamenoext)
        tb_id = re.sub(r'[^A-Za-z0-9]', '_', tb_id)

        self._metadata.update({
            'path': path,
            'absolute_path': absolute_path,
            'file_path': file_path,
            'tb_id': tb_id,
            'basename': filenamenoext,
            'filename': self._filename
        })

        self.set_time(self._timetuple)

        config = self._request.get_configuration()

        fileext = os.path.splitext(self._filename)
        if fileext:
            fileext = fileext[1][1:]
        eparser = config['extensions'][fileext]
        entrydict = eparser(self._filename, self._request)

        # Update the _metadata directly skipping over this class'
        # dict-like stuff. Otherwise we end up in a vicious loop!
        self._metadata.update(entrydict)
        self.__populated = 1
