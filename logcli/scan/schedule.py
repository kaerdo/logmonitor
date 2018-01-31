#!/usr/bin/env python
# -*-coding:utf8-*-

from .count import CountHandle
from .notifyer import Notifyer
from watchdog.observers import Observer
from .watch import WatcherHandler
from .rule import Rulehandle

class scheduler:
    def __init__(self):
        self.count = CountHandle()
        self.notify = Notifyer()
        self.watchers = {}
        self.handles = {}
        self.observer = Observer()

    def add_monitor(self, filename, rule_str):
        handler = self.handles.get(filename)
        if not handler:
            self.add_watch(filename)
            handler = self.handles.get(filename)
        handler.monitor.add(Rulehandle.load(rule_str))

    def del_monitor(self, filename, rulename):
        handler = self.handles.get(filename)  
        if not handler:
            return
        handler.monitor.delete(rulename)

    def add_watch(self, filename):
        # watch 
        if filename not in self.handles:
            handler = WatcherHandler(filename, self.count, self.notify)
            if filename not in self.watchers:
                self.watchers[handler.filename] = self.observer.schedule(handler, handler.filename, recursive=False)
        else:
            watch = self.watchers[handler.filename]
            self.observer.add_handler_for_watch(handler, watch)
        self.handles.update({handler.filename: handler})
        handler.start()

    def del_watch(self, filename):
        if filename in self.handles:
            handler = self.handles.pop(filename)
            if handler is not None:
                watch = self.watchers[handler.filename]
                self.observer.remove_handler_for_watch(handler, watch)
                handler.stop()
                if not self.observer._handlers[watch]:
                    self.observer.unschedule(watch)
                    self.watchers.pop(handler.filename)

    def start(self):
        self.observer.start()
        self.notify.start()

    def stop(self):
        self.observer.stop()
        for handler in self.handles.values():
            handler.stop()
        self.notify.stop()

    def join(self):
        self.observer.join()
