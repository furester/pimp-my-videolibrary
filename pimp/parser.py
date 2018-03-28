from collections import defaultdict
import numpy as np
from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
from hachoir_metadata.metadata_item import (QUALITY_BEST)
from sys import argv, stderr, exit


class Parser:
    _file_path = None
    _file_data = {}
    _parser = None

    def __init__(self, file_path):
        self._file_path = file_path
        self._parser = createParser(unicode(self._file_path, "utf-8"), self._file_path)
        if not self._parser:
            stderr("Unable to parse file: " + self._file_path)

    def extractInfo(self):
        # with parser:
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
        _data_compare = ["width", "nb_channel"]
        for k in _data_compare:
            if self._file_data[k] == parser._file_data[k]:
                return True
        return False

    def getInfo(self):
        return self._file_data

    def levenshtein(self, target, source=None):
        if source is None:
            source = self._file_path
        if len(source) < len(target):
            return self.levenshtein(source, target)
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
