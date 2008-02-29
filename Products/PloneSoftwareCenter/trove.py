"""
Trove reader
$Id:$
"""
from urllib2 import urlopen
from urllib2 import URLError
import socket
from itertools import groupby

PYPI_CLASSIFIERS_URL = 'http://pypi.python.org/pypi?%3Aaction=list_classifiers'

class TroveClassifier(object):
    """PloneSoftware-friendly Trove provider
    """

    def __init__(self, default=None):
        self.default = default
        try:
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)
            try:
                trove = urlopen(PYPI_CLASSIFIERS_URL)
            finally:
                socket.setdefaulttimeout(old_timeout)
        except URLError:  # no web connection
            # if it has failed, we will use the saved one
            trove = open(self.default)
        try:
            self._data = sorted([line.strip() for line in 
                                 trove.readlines()])
        finally:
            trove.close()
        self._build()

    def _make_id(self, field):
        """Make id."""
        return field.lower().replace(' ', ''), field

    def _build(self):
        """Builds unique ids."""
        ids = {}
        for line in self._data:
            split = line.split(' :: ')
            i = -1
            id_, title = self._make_id(split[i])
            while id_ in ids:
                i -= 1
                id_ = '%s %s' % (split[i], id_)
                id_, title = self._make_id(id_)
            ids[line] = id_, title
        self._ids = ids

    def get(self):
        """Returns data."""
        return self._data

    def get_datagrid(self):
        """Returns a datagrid-like structure."""
        def _sorted(key1, key2):
            key1 = key1.split('|')[-1]
            key2 = key2.split('|')[-1]
            return cmp(key1, key2)

        return sorted(['%s|%s|%s' % (value[0], value[1], key) 
                       for key, value in self._ids.items()], _sorted)

