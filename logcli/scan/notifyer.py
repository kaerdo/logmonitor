#!/usr/bin/env python
# -*-coding:utf8-*-

from Queue import Queue, Full, Empty
from threading import Thread, Event, 
import pymysql

class Message:
    def __init__(self, count, **kargs):
        # dict 
        self.contacts = kargs.get("contacts")
        # namedtuple 
        self.threshold = kargs.get("threshold")
        self.rulename = kargs.get("rulename")
        self.count = count


''' 
Table:

CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `count` int(11) DEFAULT NULL,
  `maxthreshold` int(11) DEFAULT NULL,
  `minthreshold` int(11) DEFAULT NULL,
  `rulename` varchar(20) DEFAULT NULL,
  `mail` varchar(20) DEFAULT NULL,
  `mobile` bigint(20) DEFAULT NULL,
  `is_send` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB

'''

class Notifyer:
    def __init__(self):
        self.event = Event()
        self.queue = Queue(1000)

    # pymysql 线程安全级别为1 Threads may share the module, but not connections
    def initdb(self):
        dbcon = {
            "host": '127.0.0.1', 
            "port": 3306, 
            "user": 'test123', 
            "passwd": 'test123', 
            "db": 'logscan', 
            "charset": 'utf8'
        }
        return pymysql.connect(**dbcon)

    def notify(self, message):
        conn = self.initdb()
        cursor = conn.cursor()
        sql = "insert into message(count,maxthreshold,minthreshold,rulename,mail,mobile) values({},{},{},'{}','{}',{})".format(message.count, \
                            message.threshold.max, message.threshold.min, message.rulename, \
                            message.contacts.get("mail"), message.contacts.get("mobile"))
        cursor.execute(sql)
        conn.commit()
        reqID = cursor.lastrowid
        try:
            self.queue.put_nowait(reqID)  
        except Full:
            pass  

    def start(self):
        t = Thread(target=self.sender, name="sender01")
        t.daemon = True
        t.start()

    def sender(self):
        while not self.event.is_set():
            try:
                reqID = self.queue.get(block=True, timeout=60)
            except Empty:
                continue
            conn = self.initdb()
            cursor = conn.cursor()
            sql = "select * from message where id={}".format(reqID)
            cursor.execute(sql) 
            result = cursor.fetchone()
            print result
#           for item in ["send_mail", "send_mobile"]:
#                    pass 

    def send_mail(self, message):
        pass 

    def send_mobile(self, message):
        pass  

    def stop(self):
        self.event.set()


if __name__ == '__main__':
    from collections import namedtuple

    Threshold = namedtuple('Threshold', ['min', 'max'])
    threshold = Threshold(min=5, max=10)
    kargs = {
        "contacts": {"mail": "xxxx", "mobile": "135111111"},
        "threshold": threshold,
        "rulename": "OK"
    }
    message1 = Message(15, **kargs)
    n = Notifyer()
    n.start()
    n.notify(message1)
    n.notify(message1)
    n.notify(message1)
    n.notify(message1)
    n.notify(message1)
    import time
    time.sleep(100)