#!/usr/bin/env python
# -*-coding:utf8-*-

from threading import Thread, Event 
from .notifyer import Message 

class Checker:
    def __init__(self, count, filename, rule, notify):
        self.count = count 
        self.rule = rule 
        self.filename = filename
        self.event = Event()
        self.notify = notify

    def check(self):
        while not self.event.is_set():
            self.event.wait(self.rule.interval * 60)
            count = self.count.get(self.filename, self.rule.name)
            if count > self.rule.threshold.min and count < self.rule.threshold.max:
                self.notify.notify(Message(self.count, contacts=self.rule.contacts, \
                       threshold=self.rule.threshold, rulename=self.rule.rulename))
            self.count.clean(self.filename, self.rule.name)

    def start(self):
        t1 = Thread(target=self.check, name="checker-{}-{}".format(self.filename, self.rule.name)) 
        t1.daemon = True
        t1.start()

    def stop(self):
        self.event.set() 
        self.count.remove(self.filename, self.rule.name)
