#!/usr/bin/env python
# -*-coding:utf8-*-

import re 

class Matcher:

    def __init__(self, filename, rule, count):
        self.filename = filename 
        self.expression = rule.expression
        self.rulename = rule.name
        self.count = count
        self.single = False 

    def match(self, line):
        if not self.expression:
            self.expression = r'(?P<IP>\S+) - - .+"(?P<METHOD>\w+) (?P<REQURL>\S+) .+".*'
        rule = re.compile(self.expression)
        match_result = rule.match(line)
        if match_result:
            self.count.inc(self.filename, self.rulename)

