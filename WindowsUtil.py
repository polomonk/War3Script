# -*- coding: UTF-8 -*-
import os

from Action import *


# 打印所有活动窗口
def print_all_windows():
    all_windows = pyautogui.getAllWindows()
    for win32Window in all_windows:
        print("活动窗口:", win32Window)


# 打印所有活动标题
def print_all_titles():
    all_titles = pyautogui.getAllTitles()
    for title in all_titles:
        print("活动标题:{0}".format(title))


def write_file(self, lines: list):
    pass
    with open('testfile.txt', 'a') as file:
        file.writelines(lines)  # 向文件中追加字符串列表
    os.system('xx.py')


def open_platform():
    # todo open platform
    pass


def get_window_center(window: BaseWindow):
    if window is None:
        return 0, 0
    return window.left + window.width // 2, window.top + window.height // 2


platform_window_title = "UP对战平台"
war3_window_title = "Warcraft III"
doc_window_title = "网易有道词典"


class Instance(object):
    def __init__(self):
        self.war3_window: Optional[BaseWindow] = None
        self.platform_window: Optional[BaseWindow] = None

    def get_war3_window(self):
        if self.war3_window is None or not self.war3_window.isActive:
            windows = pyautogui.getWindowsWithTitle(war3_window_title)
            if len(windows) == 0:
                Log.w("not get war3 window")
                self.war3_window = None
                return None
            self.war3_window = windows[0]
        return self.war3_window

    def get_platform_window(self):
        if self.platform_window is None:
            windows = pyautogui.getWindowsWithTitle(platform_window_title)
            if len(windows) == 0:
                Log.w("not get platform window")
                self.platform_window = None
                return None
            else:
                w = windows[0]
                for window in windows:
                    if window.width > w.width:
                        w = window
            self.platform_window = w
        return self.platform_window

    def get_platform_room_window(self):
        windows = pyautogui.getWindowsWithTitle(platform_window_title)
        if len(windows) < 2:
            Log.w("not get platform room window")
            return None
        else:
            w = windows[0]
            for window in windows:
                if window.width < w.width:
                    w = window
        return w


instance = Instance()
# # 获取活动窗口的标题
if __name__ == "__main__":
    # print_all_windows()
    # window = pyautogui.getWindowsWithTitle("C:\\")[0]
    # window.activate()
    print(instance.get_platform_room_window())
    print(instance.get_platform_window())
