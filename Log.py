open_log = True


def d(string: str):
    if open_log:  # 白色
        print(string)


def i(string: str):
    if open_log:  # 绿色
        print("\033[1;32m" + string + "\033[0m")


def w(string: str):
    if open_log:  # 黄色
        print("\033[1;33m" + string + "\033[0m")


def e(string: str):
    if open_log:  # 红色
        print("\033[1;31m" + string + "\033[0m")
