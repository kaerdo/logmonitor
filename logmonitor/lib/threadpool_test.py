#!/usr/bin/env python
# -*- coding:utf-8 -*-

from threadpool import BaseWorker, BaseWorkerManager, BaseTask

import time 

class SleepTask(BaseTask):
    def do_task(self):
        num = self.parameter.get('num', 10)
        print num
        time.sleep(num)
        print "done......."


class Worker(BaseWorker):
    def work_process(self, task):
        task.do_task() 


class WorkerManager(BaseWorkerManager):
    _baseworker = Worker
    _deadline = 60
    _keep_alive = 10

    @classmethod
    def get_pool(cls, workerMaxNum=10):
        return cls(workerMaxNum) 


if __name__ == '__main__':
    pool = WorkerManager.get_pool()
    t = SleepTask(0, num=5)
    for i in range(50):
        pool.add_task(t)
    pool.stop()
    time.sleep(100)



