from typing import Optional

open_log = True

class LogUtil:
    def __init__(self):
        self.last_log = Optional[str] = None

    def is_same_log(self):
        if self.last_log is not None:
            self.last_log = None
            return True
        return False


instance = LogUtil()


def d(string: str):
    if open_log:  # 白色
        if instance.is_same_log():
            print("", end=".")
            return
        print(string)


def i(string: str):
    if open_log:  # 绿色
        if instance.is_same_log():
            print("", end=".")
            return
        print("\033[1;32m" + string + "\033[0m")


def w(string: str):
    if open_log:  # 黄色
        if instance.is_same_log():
            print("", end=".")
            return
        print("\033[1;33m" + string + "\033[0m")


def e(string: str):
    if open_log:  # 红色
        if instance.is_same_log():
            print("", end=".")
            return
        print("\033[1;31m" + string + "\033[0m")
