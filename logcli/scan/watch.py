#!/usr/bin/env python
# -*-coding:utf8-*-

import logging
from os import path
from Queue import Queue, Full
from watchdog.events import FileSystemEventHandler
from .monitor import Monitor

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, filename, counter, notifier, queue_len=1000):
        self.filename = filename
        self.queue = Queue(queue_len)
        self.counter = counter
        self.monitor = Monitor(filename, self.queue, counter, notifier)
        self.fd = None
        self.offset = 0
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def start(self):
        self.monitor.start()

    def stop(self):
        if self.fd is not None and not self.fd.closed:
            self.fd.close()
        self.monitor.stop()

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
            self.fd.seek(self.offset, 0)
            for line in self.fd:
                line = line.rstrip('\n')
                try:
                    self.queue.put_nowait(line)
                except Full:
                    logging.warning('queue overflow')
            self.offset = self.fd.tell()

    def on_created(self, event):
        if path.abspath(event.src_path) == self.filename and path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def __eq__(self, other):
        return self.filename == other.filename

    def __ne__(self, other):
        return self.filename != other.filename

    def __hash__(self):
        return hash(self.filename)
