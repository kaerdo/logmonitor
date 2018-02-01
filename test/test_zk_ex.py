#!/usr/bin/env python
# -*-coding:utf8-*-

from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch, DataWatch
import os 
from threading import Event, Thread
from base64 import urlsafe_b64decode, urlsafe_b64encode

zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()
basedir = '/logmonitor'
files = set()

def watch_datas(data, stat, event):
    print "#########"
    print data
    print stat
    print event
    print "#########"


def watch_files(children):
    zkfiles = set(children)
    addfiles = zkfiles.difference(files)
    files.update(addfiles) 
    for i in addfiles:
        DataWatch(zk, os.path.join(basedir, i), watch_datas)

def main():
    ChildrenWatch(zk, basedir, watch_files)


if __name__ == '__main__':
    main()
    import time 
    time.sleep(1000)

