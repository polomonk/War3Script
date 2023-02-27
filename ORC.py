import difflib
import random

import pyautogui
from PIL import Image
from pygetwindow import BaseWindow
from pytesseract import pytesseract

import ImageUtil
import Log
import WindowsUtil


def is_string_match(string1, string2) -> bool:
    result = difflib.SequenceMatcher(None, string1, string2).quick_ratio()
    # Log.i(string1 + " : " + string2 + "\rconfidence:" + str(result))
    return result > 0.5


def region_text(left, top, width, height) -> list[type(str)]:
    # img = pyautogui.screenshot(ImageUtil.images_root + "temp\\test.png", region=(left, top, width, height))
    img = pyautogui.screenshot(None, region=(left, top, width, height))
    matrix = (1, 0, 0, 0,
              0, 0, 0, 0,
              0, 0, 1, 0)
    img = img.convert("L", matrix)
    img.save(ImageUtil.images_root + "temp\\test" + str(random.randint(1, 6)) + ".png")
    text = pytesseract.image_to_string(img, lang="chi_sim", config="--psm 1") \
        # .split("\n")
    Log.d(text)
    return text


def get_message(x_left: int, y_bottom: int, line_height: int, width=250, rows: int = 1) -> list[type(str)]:
    Log.d(
        "  x:" + str(x_left) + "  y:" + str(y_bottom - line_height * rows) + "  width:" + str(width) + "  height:" + str(
            line_height * rows))
    lines = []
    for i in range(rows):
        lines.append(str(region_text(x_left, y_bottom - line_height * rows, width, line_height)))
    return lines


def get_window_message(window: BaseWindow, x_left: int, y_bottom: int, line_height: int, width=250, rows: int = 1) \
        -> list[type(str)]:
    return get_message(window.left + x_left, window.top + y_bottom, line_height, width, rows)


# war3 message in bottom(82, 582)  行高 23
def get_system_message(rows: int = 1) -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 82, 582, 23, rows)


# player message in bottom(86, 634)  行高 21
def get_player_message(rows: int = 1) -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 86, 634, 21, rows)


# hero message (928, 160)  行高 21
def get_hero_message(rows: int = 4) -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 928, 160, 25, width=340, rows=rows)


if __name__ == '__main__':
    import time

    # 722, 694
    while True:
        lines = get_message(722, 694, 23, 3)
        print(lines)
        time.sleep(1)
