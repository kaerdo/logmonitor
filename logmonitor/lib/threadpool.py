#!/usr/bin/env python
# -*- coding:utf-8 -*-

from threading import Condition, Thread, Lock
from collections import deque, OrderedDict
import time 
import traceback 
import logging

class BaseWorker(Thread):

    def __init__(self, workermanager):
        Thread.__init__(self)
        self.workermanager = workermanager
        self.__running = True
        self.__task = None 

    def work_process(self, task):
        pass
        # task.do_task() 

    def task_exec(self):
        self.__task = self.workermanager.get_task()
        while self.__task:
            self.work_process(self.__task)
            with self.workermanager.queueLock:
                self.workermanager.taskTotalNum -= 1
            self.__task = self.workermanager.get_task()

    def run(self):
        try:
            self.task_exec()
        except Exception as e: 
            error_info = traceback.format_exc()
            # logging and notify 
            print "task:{} {} -- {}".format(self.__task, e, error_info)

    def stop(self):
        self.__running = False 
        # logging and notify 

class BaseWorkerManager:

    _baseworker = BaseWorker
    __single = None
    __init = True
    _deadline = 60
    _keep_alive = 30 

    def __new__(cls, *k, **args):
        if not BaseWorkerManager.__single:
            BaseWorkerManager.__single = object.__new__(cls)
        return BaseWorkerManager.__single

    """ 
    优先级为 0，1，2 由高至低
    """
    def __init__(self, workerMaxNum):
        if self.__class__.__init:
            self.workerMaxNum = workerMaxNum
            self.workerCur = []
            self.priorityQueue = OrderedDict()
            self.taskQueueNum = 0
            self.taskTotalNum = 0
            self.last_full = -1 
            self.next_dump_time = -1
            self.workLock = Lock()
            self.queueLock = Condition()
            for pipe in range(3):
                self.priorityQueue[pipe] = deque()
            self.__class__.__init = False

    def add_task(self, task):
        taskPriority = getattr(task, 'priority')
        if taskPriority == None or taskPriority not in [0, 1, 2]:
            return "It is not a task, or do not conform to the specification.."
        with self.queueLock:
            self.priorityQueue[taskPriority].appendleft(task)
            self.taskQueueNum += 1 
            self.taskTotalNum += 1
            taskTotal = self.taskTotalNum
            self.queueLock.notify(1)
        self.__schedule(taskTotal)

    def get_task(self):
        with self.queueLock:
            if self.taskQueueNum <= 0:
                self.queueLock.wait(self._keep_alive)
            if self.taskQueueNum > 0:
                now = time.time()
                reptask = None 
                notimeout_queue = OrderedDict()
                for priority, queue in self.priorityQueue.items():
                    if len(queue) > 0:
                        task = queue.pop() 
                        if now - task.now >= self._deadline:
                            reptask = task
                            break
                        else:
                            notimeout_queue[priority] = task

                if not reptask:
                    reptask = notimeout_queue.pop(notimeout_queue.keys()[0]) 
                self.taskQueueNum -= 1

                if notimeout_queue:
                    for priority, task in notimeout_queue.items():
                        self.priorityQueue[priority].append(task)
                return reptask

    def log(self, *info, **kargs):
        assert len(info) > 0 
        func = kargs.get('func', logging.info)
        func(info[0])

    def __schedule(self, taskTotal):
        worker = None 
        jam_duration = -1 
        with self.workLock:
            if taskTotal <= len(self.workerCur):
                self.last_full = -1  
            elif len(self.workerCur) <= self.workerMaxNum:
                worker = self._baseworker(self)
                self.workerCur.append(worker)
            else:
                now = time.time()
                if self.last_full < 0:
                    self.last_full = now
                    self.next_dump_time = now + 300.0 # 5 minutes
                    return
                if now > self.next_dump_time:
                    self.next_dump_time = now + 1.0
                    jam_duration = now - self.last_full 
        if worker:
            worker.start()
        if jam_duration > 0:
            """
            设置notify and logging
            """
            print "jam_duration...."

    def stop(self):
        with self.workLock:
            for worker in self.workerCur:
                self.last_full = -1
                worker.stop()
                self.workerCur.remove(worker)

    @classmethod
    def get_pool(cls, workerMaxNum=10):
        return cls(workerMaxNum) 

class BaseTask:
    def __init__(self, priority, **kargs):
        self.now = time.time()
        self.priority = priority
        self.parameter = {}
        if kargs:
            self.parameter.update(kargs)

    def do_task(self):
        pass 

