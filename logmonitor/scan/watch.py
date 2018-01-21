#!/usr/bin/env python
# -*-coding:utf8-*-

from os import path 
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import match 

class watcher(FileSystemEventHandler):
    def __init__(self, filename, matcher):
        self.filename = path.abspath(filename) 
        self.matcher = matcher
        self.observer = Observer()
        self.fd = None 
        self.offset = 0 
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_created(self, event):
        if path.abspath(event.src_path) == self.filename and path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_deleted(self, event):
        if path.abspath(event.src_path) == self.filename:
            self.fd.close() 

    def on_moved(self, event):
        if path.abspath(event.src_path) == self.filename:
            self.fd.close()
        if path.abspath(event.dest_path) == self.filename and path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename) 

    def on_modified(self, event):
        if path.abspath(event.src_path) == self.filename:
            match = getattr(self.matcher, 'match', lambda line: False)
            self.fd.seek(self.offset, 0)
            for line in self.fd:
                line = line.strip('\n')
                if match(line):
                    print line 
            self.offset = self.fd.tell()

    def start(self):
        self.observer.schedule(self, path.dirname(self.filename), recursive=False)
        self.observer.start()
        self.observer.join()

    def stop(self):
        self.observer.stop()
