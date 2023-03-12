from abc import ABC
from typing import Optional
from colorama import Fore, Back, Style

open_log = True
last_log = ""


def print_log(message: str, color: Fore = Fore.WHITE) -> str:
    global last_log
    if not open_log:
        return ""
    if message == last_log or message == "":
        return ""
    last_log = message
    print(color + message)


def d(message: str):
    print_log(message)


def i(message: str):  # 绿色
    print_log(message, Fore.GREEN)


def w(message: str):  # 黄色
    print_log(message, Fore.YELLOW)


def e(message: str):  # 红色
    print(message, Fore.RED)
