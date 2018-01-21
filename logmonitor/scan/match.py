#!/usr/bin/env python
# -*-coding:utf8-*-

import re 

class MatcherBase:
    __Single = None  
    __init = True 

    def __new__(cls, *k, **args):
        if MatcherBase.__Single:
            MatcherBase.__Single = object.__new__(cls)
        return MatcherBase.__Single

    def __init__(self, rule=None):
        if self.__class__.__init:
            self.rule = rule 
            self.__class__.__init = False

    def match(self):
        return  

class Matcher(MatcherBase):
    def match(self, line):
        if not self.rule:
            self.rule = r'(?P<IP>\S+) - - .+"(?P<METHOD>\w+) (?P<REQURL>\S+) .+".*'
        rule = re.compile(self.rule)
        match_result = rule.match(line)
        if match_result:
            Match = match_result.groupdict()
            return Match.values() 

