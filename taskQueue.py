import heapq
import sys
import threading
import time
import uuid
from queue import Queue


class PriorityQueue:
    """
    自己实现的优先级队列，使用了Python的堆
    """

    def __init__(self):
        self._index = 0
        self.queue = []

    def enqueue(self, priority, val):
        heapq.heappush(self.queue, (priority, self._index, val))
        self._index += 1

    def dequeue(self):
        return heapq.heappop(self.queue)[-1]

    @property
    def empty(self):
        return len(self.queue) == 0


class Priority:
    HIGH = 0
    MIDDLE = 1
    LOW = 2


class Task:
    def __init__(self, func, callback=None, priority=Priority.MIDDLE, args=(), kwargs={}):
        """
        Args:
            func: 需要执行的函数
            callback:  执行完的回调函数
            priority: 优先级
            *args:
            **kwargs:
        """
        self._id = uuid.uuid4().hex
        self.function = func
        self.callback = callback
        self.priority = priority
        self.args = args
        self.kwargs = kwargs

    @property
    def id(self):
        return self._id

    def run(self):
        try:
            if self.callback:
                # 回调函数原型 callback(task_obj, result)
                result = self.callback(self, self.function(*self.args, **self.kwargs))
            else:
                result = self.function(*self.args, **self.kwargs)
            return result
        except Exception as e:
            if self.callback:
                result = self.callback(self, e)
            else:
                result = e
            return result


class TaskQueue:
    """
    基于线程的异步任务队列
    """

    def __init__(self, output_redirect=False):
        self.queue = PriorityQueue()
        self.output_redirect = output_redirect
        self._redirect_objs = {}
        self._results = {}

    def put(self, task: Task):
        """
        将task加入任务列表
        Args:
            task:
        Returns:返回task id
        """
        self.queue.enqueue(task.priority, task)
        return task.id

    def get(self):
        return self.queue.dequeue()

    def run(self):
        while not self.queue.empty:
            task = self.get()
            # 开启新线程
            t = threading.Thread(target=self._task_wrapper, name=task.id, args=[task])
            self._log(f'Start thread {task.id}')
            t.start()

    def get_result(self, task_id: str):
        return self._results.get(task_id, None)

    @staticmethod
    def _log(msg: str):
        """日志输出接口，可以替换为日志组件"""
        print(f'[TaskQueue] {msg}')

    def _task_wrapper(self, task: Task):
        if self.output_redirect:
            result = task.run()
            self._log(f'Task finished. {task.id}')
        else:
            result = task.run()

        # 保存结果
        self._results[task.id] = result


if __name__ == '__main__':
    task_queue = TaskQueue(output_redirect=True)


    def fun1():
        time.sleep(2)
        return 1


    task_queue.put(Task(
        func=fun1,
        callback=lambda task, result: print(f'task1 result: {result}'),
    ))


    def fun3(num1, num2):
        print(f'num1={num1}')
        print(f'num2={num2}')
        return num1 + num2


    def callback(task_obj, result):
        print(f'task3 result={result}')


    task_queue.put(Task(func=fun3, callback=callback, args=[2, 3]))

    task_queue.run()
