# -*- coding: utf-8 -*-

import sqlite3
import hashlib
import os

class Storage:
    _cache_path = './var/cache'
    _conn = None
    _cursor = None

    def __init__(self):
        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        # TODO manage directory not accessible
        # if not os.access(self._cache_path, os.W_OK):
        #     os.makedirs(self._cache_path)

        self._conn = sqlite3.connect('%s/example.db' % self._cache_path)
        self._cursor = self._conn.cursor()
        self.initializeTables()

    def storeMovieMetadata(self, main_id, filename, meta):
        m = hashlib.md5()
        m.update(filename)
        id = m.hexdigest()

        # Insert a row of data
        try:
            self._cursor.execute(
                "INSERT INTO movie_metadata VALUES ('%s','%s','%s','%s','%s','%s','%d','%d','%d','%d')".format(id, main_id, filename, meta['compression'], meta.get('bits_per_sample', 0), meta['bits_per_pixel'], meta['height'], meta['width'], meta['bit_rate'], meta['sample_rate'])
            )
        except sqlite3.IntegrityError as exc:
            return id

        # Save (commit) the changes
        self._conn.commit()

        return id

    def initializeTables(self):
        movie_metadata = '''CREATE TABLE IF NOT EXISTS movie_metadata
                (id text PRIMARY KEY, main_id text, filename text, compression text,
                bits_per_sample text, bits_per_pixel text, height int, width int,
                bit_rate int, sample_rate int)
        '''
        tables = [movie_metadata]

        for table in tables:
            self._cursor.execute(table)
