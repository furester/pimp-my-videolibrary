# -*- coding: utf-8 -*-

import os, glob
import parser


class Retriever:
    _start_path = None
    _ext = []
    _cache_enabled = True
    _storage = None

    def __init__(self, file_path, ext, storage):
        self._start_path = file_path
        self._ext = ext
        self._storage = storage

    def retrieveFileList(self, force_cache=False):
        list_file = []
        if force_cache:
            print("Retrieving from cache only")
            all_file = self._storage.retrieveAllFileName()
            return all_file

        for path, dirs, files in os.walk(self._start_path):
            for filename in files:
                if filename.endswith(tuple(self._ext)):
                    f = self.writeCache(os.path.join(path, filename))
                    if f is not None:
                        list_file.append(f)

        return list_file

    def cacheEnabled(self, flag):
        self._cache_enabled = flag

    def writeCache(self, f):
        if self._storage is None:
            return f

        try:
            # initialize parser
            main_parser = parser.Parser(f)
        except TypeError as exc:
            print("TypeError: {} for {}".format(exc, f))
            return None
        except Exception as err:
            print("Generic Exception: {} for {}".format(err, f))
            return None

        try:
            # extract metadata
            main_parser.extractInfo()
        except TypeError as exc:
            print("TypeError on extract: {} for {}".format(exc, f))
            return None

        self._storage.storeMovieMetadata(f, main_parser.getInfo())
        return f

    def readCache(self, file_path, ext):
        return None
