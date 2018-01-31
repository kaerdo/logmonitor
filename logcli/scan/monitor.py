#!/usr/bin/env python
# -*-coding:utf8-*-

from threading import Thread, Event 
from .matcher import Matcher
from .check import Checker
from Queue import Empty

class Monitor:
    def __init__(self, filename, queue, count, notify):
        self.queue = queue
        self.count = count
        self.filename = filename
        self.event = Event()
        self.matchers = {}
        self.checkers = {} 
        self.notify = notify

    def __add_matcher(self, rule):
        matcher = Matcher(self.filename, rule, self.count)
        return matcher  

    def __add_checker(self, rule):
        checker = Checker(self.count, self.filename, rule, self.notify) 
        checker.start()
        return checker

    def add(self, rule):
        self.matchers.update({rule.name: self.__add_matcher(rule)})
        self.checkers.update({rule.name: self.__add_checker(rule)})

    def __del_matcher(self, rulename):
        self.matchers.pop(rulename)

    def __del_checker(self, rulename):
        checker = self.checkers.pop(rulename)
        checker.stop()

    def delete(self, rulename):
        self.__del_matcher(rulename)
        self.__del_checker(rulename)

    def do_match(self):
        while not self.event.is_set():
            try:
                line = self.queue.get(block=True, timeout=30)
            except Empty:
                continue 
            for matcher in self.matchers.values():
                matcher.match(line) 

    def start(self):
        t = Thread(target=self.do_match, name="thread-{}".format(self.filename)) 
        t.daemon = True
        t.start()

    def stop(self):
        self.event.set()
