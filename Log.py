import sys
from abc import ABC
import time
from typing import Optional
from colorama import Fore, Back, Style, init

open_log = True
init(autoreset=True)
last_log = ""
console = sys.stdout


def redirection_to_console():
    sys.stdout = console


def redirection_to_file(file_path):
    f = open(file_path, "a+")
    sys.stdout = f


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S".format(time.localtime()))


def print_log(message: str, color=Fore.WHITE) -> str:
    global last_log
    if not open_log:
        return ""
    if message == last_log or message == "":
        return ""
    last_log = message
    print(color + get_time() + "\t" + message)


def d(message: str):
    print_log(message)


def i(message: str):  # 绿色
    print_log(message, Fore.GREEN)


def w(message: str):  # 黄色
    print_log(message, Fore.YELLOW)


def e(message: str):  # 红色
    print_log(message, Fore.RED)


if __name__ == '__main__':
    redirection_to_file("log.txt")
    d("debug")
    i("info")
    w("warning")
    e("error")
