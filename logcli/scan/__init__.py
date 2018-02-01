#!/usr/bin/env python
# -*-coding:utf8-*-

from threading import Event
from kazoo.client import KazooClient, NoNodeError
from kazoo.recipe.watchers import ChildrenWatch, DataWatch
from .schedule import scheduler
from os import path
from functools import partial
from base64 import urlsafe_b64decode

class Config:
    def __init__(self, addr, root):
        self.addr = addr 
        self.root = root 

    @classmethod
    def loads(cls, *config):
        return cls(*config)

class Scan:
    def __init__(self, config):
        self.__event = Event() 
        self.zk = KazooClient(hosts=config.addr)
        self.schedule = scheduler()
        self.root = config.root 
        self.files = set()
        self.rules = {}
        self.file_watchers_ctl = {}
        self.rule_watchers_ctl = {}

    def __make_key(self, filename):
        return path.abspath(urlsafe_b64decode(filename.encode()))

    def watch_data(self, data, stat, zk_event, filename, name, event):
        if zk_event and zk_event.type == 'CHANGED':
            self.schedule.del_monitor(self.__make_key(filename), name)
            self.schedule.add_monitor(self.__make_key(filename), data)
        return not event.is_set()

    def watch_rules(self, children, filename, event):
        if event.is_set():
            return False
        zkrules = set(children)
        addrules = zkrules.difference(self.rules.get(filename, set()))
        v = self.rules.get(filename, set())
        v.update(addrules)
        self.rules[filename] = v

        for rule in addrules:
            rulenode = path.join(self.root, filename, rule)
            self.schedule.add_monitor(self.__make_key(filename), self.zk.get(rulenode)[0])
            self.rule_watchers_ctl[rule] = Event()
            fn = partial(self.watch_data, filename=filename, name=rule, event=self.rule_watchers_ctl[rule])
            try:
                DataWatch(self.zk, rulenode, fn)
            except NoNodeError:
                pass

        delrules = self.rules.get(filename, set()).difference(zkrules)
        for rule in delrules:
            self.schedule.del_monitor(self.__make_key(filename), rule)
            self.rule_watchers_ctl.pop(rule).set()
            v = self.rules.get(filename, set())
            v.remove(rule)
            self.rules[filename] = v

    def watch_files(self, children):
        if self.__event.is_set():
            return False
        zkfiles = set(children)
        addfiles = zkfiles.difference(self.files) 
        self.files.update(addfiles)
        for file in addfiles:
            self.schedule.add_watch(self.__make_key(file))
            self.file_watchers_ctl[file] = Event()
            fn = partial(self.watch_rules, filename=file, event=self.file_watchers_ctl[file])
            ChildrenWatch(self.zk, path.join(self.root, file), fn) 

        delfiles = self.files.difference(zkfiles) 
        for file in delfiles:
            self.schedule.del_watch(self.__make_key(file))
            event = self.file_watchers_ctl.pop(file)
            event.set()
            self.files.remove(file)

    def start(self):
        self.zk.start()
        ChildrenWatch(self.zk, self.root, self.watch_files)
        self.schedule.start()

    def stop(self):
        for e in self.rule_watchers_ctl.values():
            e.set()
        for e in self.file_watchers_ctl.values():
            e.set()
        self.zk.stop()
        self.schedule.stop()
        self.__event.set()

    def join(self):
        self.__event.wait()
