# -*- coding: utf-8 -*-

from collections import defaultdict
import numpy as np
import re
from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
from os.path import basename
from sys import stderr


class Parser:
    _file_path = None
    _file_data = {}
    _parser = None
    _data_compare = ["height", "nb_channel", "language"]

    def __init__(self, file_path, data=None):
        self._file_data = {}
        self._file_path = file_path
        if data is not None:
            self.populate(data)
        else:
            self._parser = createParser(unicode(self._file_path, "utf-8"), self._file_path)
            if not self._parser:
                stderr("Unable to parse file: " + self._file_path)

    def populate(self, data):
        for key, value in data.iteritems():
            self._file_data[key] = value

    def extractInfo(self):
        # with parser:
        if self._parser is None:
            return
        try:
            metadata = extractMetadata(self._parser)
        except Exception as err:
            stderr("Metadata extraction error: %s" % err)
            metadata = None
        if not metadata:
            stderr("Unable to extract metadata")
        # TODO: debug with real data and delete if not necessary
        meta = defaultdict(defaultdict)
        for line in metadata.exportPlaintext(None, False):
            if isinstance(line, unicode):
                _t = line.encode("utf8")
            else:
                _t = line
            if _t.endswith(':'):
                k = _t[:-1]
            else:
                if _t.count(':') > 1:
                    _t = _t.replace(':', '|', 1).replace(':', '').replace('|', ':')
                tag, value = _t.split(': ')
                tag = tag[2:]
                meta[k][tag] = value
                self._file_data[tag] = value
        # print(self._file_data)

    def match(self, parser):
        ret = True
        for k in self._data_compare:
            if self.getInfo(k) != parser.getInfo(k):
                ret = False
                break
        return ret

    '''
    Compare two parsed file
    :param parser:
    :return: -1 current version is different and lower
              0 same version or not know
             +1 current version is different and better
    '''

    def compare(self, parser):
        ret = 0
        if self.match(parser):
            return ret
        _self_value = self.getInfo("height")
        _parser_value = parser.getInfo("height")
        if _self_value == _parser_value:
            ret = 0
        elif _self_value > _parser_value:
            ret = 1
        else:
            ret = -1
        for k in ["nb_channel", "language"]:
            if self.getInfo(k) != parser.getInfo(k):
                ret = 0
                break
        return ret

    def getInfo(self, key=None):
        if not key:
            return self._file_data
        elif key in self._file_data:
            return self._file_data[key]
        else:
            return None

    def levenshtein(self, target, source=None, clean=True):
        if source is None:
            source = self._file_path
        # remove extension
        source = basename(source)
        target = basename(target)
        if len(source) < len(target):
            return self.levenshtein(source, target, clean)
        if clean:
            # remove extension
            source = basename(source[:-4])
            target = basename(target[:-4])
            # remove all after year
            p = re.compile(".[19|20]\d{2}.")
            for m in p.finditer(source):
                source = source[:m.start()]
                break
            for m in p.finditer(target):
                target = target[:m.start()]
                break
        # So now we have len(source) >= len(target).
        if len(target) == 0:
            return len(source)
        # We call tuple() to force strings to be used as sequences
        # ('c', 'a', 't', 's') - numpy uses them as values by default.
        source = np.array(tuple(source))
        target = np.array(tuple(target))
        # We use a dynamic programming algorithm, but with the
        # added optimization that we only need the last two rows
        # of the matrix.
        previous_row = np.arange(target.size + 1)
        for s in source:
            # Insertion (target grows longer than source):
            current_row = previous_row + 1
            # Substitution or matching:
            # Target and source items are aligned, and either
            # are different (cost of 1), or are the same (cost of 0).
            current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))
            # Deletion (target grows shorter than source):
            current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)
            previous_row = current_row
        return previous_row[-1]

    def normalized_levenshtein(self, target, source=None):
        if source is None:
            source = self._file_path
        source = basename(source)
        target = basename(target)
        m_len = max(len(source), len(target))
        if m_len == 0:
            return 0
        lev = self.levenshtein(target, source)
        ret = float(lev) / m_len
        return round((1 - ret) * 100)
