#!/usr/bin/env python
# -*-coding:utf8-*-

from threading import Thread, Event

class Checker:
    def __init__(self, count, filename, rule):
        self.count = count 
        self.rule = rule 
        self.filename = filename
        self.event = Event()

    def check(self):
        while not self.event.is_set():
            self.event.wait(60)

    def start(self):
        t1 = Thread(target=self.check, name="checker-{}-{}".format(self.filename, self.rule.name)) 
        t1.daemon = True
        t1.start()

    def stop(self):
        self.event.set() 
