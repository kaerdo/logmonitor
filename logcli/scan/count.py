#!/usr/bin/env python
# -*-coding:utf8-*-

class CountHandle:

    ''' Counter for concurrent counting '''

    def __init__(self):
        self.count = {}

    def inc(self, filename, rulename):
        rules = self.count.setdefault(filename, {rulename: 0})
        num = rules.setdefault(rulename, 0) + 1
        rules[rulename] = num 
        self.count.update(rules)

    def get(self, filename, rulename):
        return self.count[filename][rulename]

    def remove(self, filename, rulename=None):
        if rulename:
            self.count[filename].pop(rulename)
        else:
            self.count.pop(filename)

    def clean(self, filename, rulename):
        try:
            self.count[filename][rulename] = 0
        except KeyError:
            raise 
