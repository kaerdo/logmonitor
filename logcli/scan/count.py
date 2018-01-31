#!/usr/bin/env python
# -*-coding:utf8-*-

class CountBase:
    __Single = None  
    __init = True 

    def __new__(cls, *k, **args):
        if CountBase.__Single:
            CountBase.__Single = object.__new__(cls)
        return CountBase.__Single

    def __init__(self):
        if self.__class__.__init:
            self.count = {} 
            self.__class__.__init = False


class CountHandle(CountBase):

    ''' Counter for concurrent counting '''

    def inc(self, filename, rulename):
        rules = self.count.setdefault(filename, {rulename: 0})
        num = rules.setdefault(rulename, 0) + 1
        rules[rulename] = num 
        self.count.update(rules)

    def get(self, filename, rulename):
        try:
            count = self.count[filename][rulename]
        except KeyError:
            return None 
        return count  

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
