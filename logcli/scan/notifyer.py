#!/usr/bin/env python
# -*-coding:utf8-*-

from Queue import Queue, Full, Empty
from threading import Thread, Event, BoundedSemaphore
import pymysql

class Message:
    def __init__(self, filename, count, **kargs):
        self.filename = filename
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
  `filename` varchar(20) DEFAULT NULL,
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
        self.__semaphore = BoundedSemaphore(5)

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
        conn = pymysql.connect(**dbcon)
        cursor = conn.cursor()
        return conn, cursor

    def notify(self, message):
        conn, cursor = self.initdb()
        sql = "insert into message(count,maxthreshold,minthreshold,rulename,mail,mobile,filename) values({},{},{},'{}','{}',{},'{}')".format(message.count, \
                message.threshold.max, message.threshold.min, message.rulename, \
                message.contacts.get("mail"), message.contacts.get("mobile"), message.filename)
        cursor.execute(sql)
        conn.commit()
        reqID = cursor.lastrowid
        try:
            self.queue.put_nowait(reqID)  
        except Full:
            pass  

    def __compensate(self):
        while not self.event.is_set():
            self.event.wait(5)
            conn, cursor = self.initdb()
            sql = "select id from message where is_send=0"
            cursor.execute(sql)
            result = cursor.fetchall()
            for item in result:
                reqID, = item
                try:
                    self.queue.put_nowait(reqID)  
                except Full:
                    pass  

    def start(self):
        t1 = Thread(target=self.__sender, name="sender01")
        t1.daemon = True
        t1.start()
        t2 = Thread(target=self.__compensate, name="compensate01")
        t2.daemon = True
        t2.start()

    def __sender_wrap(self, st, message):
        with self.__semaphore:
            st(message)
            conn, cursor = self.initdb()
            sql = "update message set is_send=1 where id={}".format(message[0])
            cursor.execute(sql) 
            conn.commit()

    def __sender(self):
        while not self.event.is_set():
            try:
                reqID = self.queue.get(block=True, timeout=60)
            except Empty:
                continue
            conn, cursor = self.initdb()
            sql = "select * from message where id={}".format(reqID)
            cursor.execute(sql) 
            result = cursor.fetchone()
            for item in dir(self.__class__):
                if item.startswith("send"):
                    st = getattr(self, item)
                    t = Thread(target=self.__sender_wrap, args=(st, result))
                    t.daemon = True
                    t.start()

    def send_mail(self, message):
        print message

    def send_mobile(self, message):
        print message  

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
    time.sleep(5)
    n.stop()