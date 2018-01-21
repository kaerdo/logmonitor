#!/usr/bin/env python
# -*-coding:utf8-*-

import shelve
from threading import Lock

class CountHandle:
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.db = shelve.open(self.dbpath, 'c')
        self.lock = Lock()

    def inc(self, filename):
        with self.lock:
            self.db[filename] = self.db.get('filename', 0) + 1

    def get(self, filename):
        return self.db.get('filename', 0)

    def remove(self, filename):
        with self.lock:
            self.db.pop(filename) 
    
    def stop(self, filename):
        with self.lock:
            self.db.close()
             