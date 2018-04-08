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

    def storeMovieMetadata(self, filename, meta):
        m = hashlib.md5()
        m.update(filename.encode('utf-8'))
        id = m.hexdigest()

        # Insert a row of data
        try:
            self._cursor.execute(
                'INSERT INTO movie_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)',
                (id,
                 unicode(filename, "utf-8"),
                 unicode(meta.get('compression', ""), "utf-8"),
                 meta.get('bits_per_sample', 0),
                 meta.get('bits_per_pixel', 0),
                 meta.get('height', 0),
                 meta.get('width', 0),
                 meta.get('bit_rate', 0),
                 meta.get('sample_rate', 0),
                 meta.get('language', ""),
                 meta.get('nb_channel', 0)
                 ))
        except sqlite3.IntegrityError as exc:
            return id


        # Save (commit) the changes
        self._conn.commit()
        return id

    def retrieveAllFileName(self):
        try:
            self._cursor.execute("SELECT filename FROM movie_metadata")
        except sqlite3.IntegrityError as exc:
            print(exc)
            return None

        return self._cursor.fetchall()

    def retrieveMovieMetadata(self, filename):
        try:
            m = hashlib.md5()
            m.update(filename.encode('utf-8'))
            id = (m.hexdigest(),)
            self._cursor.execute("SELECT * FROM movie_metadata WHERE id = ?", id)
        except UnicodeDecodeError as exc:
            print(filename)
            print(exc)
            return None
        _data = self._cursor.fetchone()

        return {
            "id": _data[0].encode("utf8"),
            "filename": _data[1].encode("utf8"),
            "compression": _data[2],
            "bits_per_sample": _data[3],
            "bits_per_pixel": _data[4],
            "height": _data[5],
            "width": _data[6],
            "bit_rate": _data[7],
            "sample_rate": _data[8],
            "language": _data[9],
            "nb_channel": _data[10]
        }

    def initializeTables(self):
        movie_metadata = '''CREATE TABLE IF NOT EXISTS movie_metadata
                (id text PRIMARY KEY, filename text, compression text,
                bits_per_sample text, bits_per_pixel text, height int, width int,
                bit_rate int, sample_rate int, language string, nb_channel int,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        '''
        tables = [movie_metadata]

        for table in tables:
            self._cursor.execute(table)
