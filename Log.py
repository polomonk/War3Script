from abc import ABC
from typing import Optional

open_log = True
last_log = ""


def log_filter(message: str) -> str:
    global last_log
    if not open_log:
        return ""
    if message == last_log or message == "":
        return ""
    last_log = message
    return message


def d(message: str):
    msg = log_filter(message)
    if msg == "":
        return
    print(msg)


def i(message: str):  # 绿色
    msg = log_filter(message)
    if msg == "":
        return
    print("\033[1;32m" + msg + "\033[0m")


def w(message: str):  # 黄色
    msg = log_filter(message)
    if msg == "":
        return
    print("\033[1;33m" + msg + "\033[0m")


def e(message: str):  # 红色
    msg = log_filter(message)
    if msg == "":
        return
    print("\033[1;31m" + msg + "\033[0m")
