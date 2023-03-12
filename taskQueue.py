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


class Redirection:
    def __init__(self, buffer_size=512):
        self.buffer = Queue(maxsize=512)
        self._console = sys.stdout
        # 自定义的输出端
        self.custom = None

    def write(self, output_stream):
        # 加入缓冲区队列
        self.buffer.put(output_stream)

    def to_console(self):
        sys.stdout = self._console
        # 出列
        while not self.buffer.empty():
            print(self.buffer.get())

    def to_file(self, file_path):
        with open(file_path, 'w+') as f:
            sys.stdout = f
            while not self.buffer.empty():
                print(self.buffer.get())
            f.close()

    def to_custom(self):
        while not self.buffer.empty():
            self.custom(self.buffer.get())

    def to_list(self):
        data = []
        while not self.buffer.empty():
            data.append(self.buffer.get())
        return data

    def flush(self):
        self.buffer.empty()

    def reset(self):
        sys.stdout = self._console


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
        # 任务运行过程的输出，stdout的输出
        self._outputs: Redirection = None

    @property
    def id(self):
        return self._id

    @property
    def outputs(self) -> Redirection:
        return self._outputs

    @outputs.setter
    def outputs(self, value: Redirection):
        self._outputs = value

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

    def get_output(self, task_id: str) -> Redirection:
        return self._redirect_objs.get(task_id, None)

    def get_result(self, task_id: str):
        return self._results.get(task_id, None)

    @staticmethod
    def _log(msg: str):
        """日志输出接口，可以替换为日志组件"""
        print(f'[TaskQueue] {msg}')

    def _task_wrapper(self, task: Task):
        if self.output_redirect:
            if task.id in self._redirect_objs:
                redirect_obj = self._redirect_objs[task.id]
            else:
                redirect_obj = Redirection(2048)
                self._redirect_objs[task.id] = redirect_obj
            # 重定向输出
            sys.stdout = redirect_obj
            task.outputs = redirect_obj
            result = task.run()
            # 恢复默认输出
            redirect_obj.reset()
            self._log(f'Task finished. {task.id}')
        else:
            result = task.run()

        # 保存结果
        self._results[task.id] = result


def fun1(num1, num2):
    print(f'num1={num1}')
    print(f'num2={num2}')
    return num1 + num2


Task(
    func=fun1,
    callback=lambda task, result: print(f'task result: {result}'),
)

# 也可以写成这样
Task(
    func=lambda num1, num2: num1 + num2,
    callback=lambda task, result: print(f'task result: {result}'),
    args=[2, 3]
)

if __name__ == '__main__':
    task_queue = TaskQueue(output_redirect=True)


    def fun1():
        time.sleep(2)
        return 1


    def fun2():
        time.sleep(3)
        return 2


    task_queue.put(Task(
        func=fun1,
        callback=lambda task, result: print(f'task1 result: {result}'),
    ))
    task_queue.put(Task(
        func=fun2,
        callback=lambda task, result: print(f'task2 result: {result}'),
    ))


    def custom_output(msg):
        print(f'[custom] {msg}')


    def fun3(num1, num2):
        print(f'num1={num1}')
        print(f'num2={num2}')
        return num1 + num2


    def callback(task_obj, result):
        print(f'task3 result={result}')
        output = task_obj.outputs
        output.custom = custom_output
        output.reset()
        output.to_custom()


    task_queue.put(Task(func=fun3, callback=callback, args=[2, 3]))

    print('task queue run')
    task_queue.run()
    print('do other things...')

    for i in range(0, 100):
        print(i * i)
