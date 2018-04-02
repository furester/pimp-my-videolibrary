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

    def retrieveFileList(self, force_cache = False):
        list = [];

        for path,dirs,files in os.walk( self._start_path ):
            for filename in files:
                if filename.endswith( tuple(self._ext) ):
                    list.append( os.path.join(path,filename) )

        return list

    def cacheEnabled(self, flag):
        self._cache_enabled = flag

    def writeCache(self, f):
        return f

    def readCache(self, file_path, ext):
        return None
