import difflib
import random

import PIL
import pyautogui
from PIL import Image
from pygetwindow import BaseWindow
from pytesseract import pytesseract

import ImageUtil
import Log
import WindowsUtil



def is_text_match(string1, string2) -> bool:
    result = difflib.SequenceMatcher(None, string1, string2).quick_ratio()
    if string1 == "" or string2 == "":
        return False
    Log.i(string1 + " : " + string2 + "\tconfidence:" + str(result))
    return result > 0.5


def is_text_left_match(string1, string2) -> bool:
    match_length = min(len(string1), len(string2))
    return is_text_match(string1[:match_length], string2[:match_length])


def region_text(left, top, width, height) -> list[type(str)]:
    # img = pyautogui.screenshot(ImageUtil.images_root + "temp\\test.png", region=(left, top, width, height))
    img = pyautogui.screenshot(None, region=(left, top, width, height))
    # 去掉128以下的像素
    img = img.point(lambda p: p > 128 and p)
    img = img.convert("L")
    # 如果像素值大于128，就加上128
    img = img.point(lambda p: p > 10 and p + 200)
    # 反色
    # img = img.point(lambda p: 255 - p)
    img.save(ImageUtil.images_root + "temp\\test" + str(random.randint(1, 6)) + ".png")
    text = str(pytesseract.image_to_string(img, lang="chi_sim", config="--psm 1")).replace(" ", "")
    if text == "":
        return []
    Log.d(text)
    return list(text)


def get_message(left: int, bottom: int, width: int, height: int) -> list[type(str)]:
    return region_text(left, bottom - height, width, height)


def get_window_message(window: BaseWindow, left: int, bottom: int, width: int, height: int) \
        -> list[type(str)]:
    if window is None:
        return []
    return get_message(window.left + left, window.top + bottom, width, height)


# war3 message in bottom(76, 588)  行高 23
def get_system_message() -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 76, 588, 350, 23*4+10)


# player message in bottom(86, 634)  行高 21
def get_player_message() -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 914, 158, 350, 120)


# hero message (928, 160)  行高 21
def get_hero_message(rows: int = 4) -> list[type(str)]:
    window = WindowsUtil.instance.get_war3_window()
    if window is None:
        return []
    lines = []
    for i in range(0, 4):
        lines.append(region_text(window.left + 928, window.top + 160 + 25 * i, 340, 25).__str__())
    return lines
    # return get_window_message(WindowsUtil.instance.get_war3_window(), 928, 160, 25, width=340, rows=rows)


# weaponSoul(89, 378)
def get_weapon_soul_message(rows: int = 1) -> list[type(str)]:
    return get_window_message(WindowsUtil.instance.get_war3_window(), 75, 589, 350, 154)


if __name__ == '__main__':
    import time

    while True:
        # lines = region_text(757, 852-25, 350, 23+4)
        # lines = pytesseract.image_to_string(PIL.Image.open(r"D:\Program Files\Project\War3Script\images\temp\233.png"),
        #                                     lang="chi_sim", config="--psm 1")
        # print("lines:" + str(lines))
        get_system_message()
        time.sleep(1)
