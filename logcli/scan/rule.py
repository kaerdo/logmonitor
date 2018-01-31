#!/usr/bin/env python
# -*-coding:utf8-*-

import json 
from collections import namedtuple

class Rulehandle:
    def __init__(self, name, threshold, expression, interval, contacts):
        self.name = name
        self.threshold = threshold
        self.expression = expression
        self.interval = interval
        self.contacts = contacts

    @classmethod
    def load(cls, config):
        conf = json.loads(config)
        Threshold = namedtuple('Threshold', ['min', 'max'])
        threshold = Threshold(min=conf["threshold"].get("min", 0), \
                       max=conf["threshold"].get("max", 0))
        conf.update({"threshold": threshold})
        return cls(**conf)
