import os.path
import time
from typing import Callable, Optional

from PIL import Image
from abc import ABC, abstractmethod

import pyautogui
from pygetwindow import BaseWindow
import ImageUtil
import Log
import WindowsUtil


class ActionComponent(ABC):
    """
    Behavior abstract class
    action(self) must implement
    timeout_processing(self) should implement

    """

    def __init__(self, sleep_after_second=0, button="LEFT", move_duration=0.1, retry_interval=1):
        super().__init__()
        self.head: ActionComponent = self       # 头节点
        self.next: Optional[ActionComponent, None] = None   # 下一个节点
        self.sleep_before_second: int = 0  # 执行前等待时间
        self.sleep_after_second: float = sleep_after_second  # 执行后等待时间
        self.button = button  # 鼠标按键
        self.move_duration = move_duration  # 鼠标移动时间
        # 异常处理
        self.retry_interval = retry_interval  # 重试间隔
        self.timeout_second = 2  # 超时时间
        self.confidence = 0.8  # 图片置信度
        self.timeout_func: Optional[Callable, None] = None  # 超时处理函数

    def set_next_action(self, next_action: "ActionComponent") -> Optional["ActionComponent"]:
        if next_action is None:
            return None
        self.next = next_action
        next_action.head = self.head  # 设置头节点
        return self.next  # 返回下一个节点

    def set_after_second(self, sleep_after_second) -> "ActionComponent":
        self.sleep_after_second = sleep_after_second
        return self

    def set_before_second(self, sleep_before_second) -> "ActionComponent":
        self.sleep_before_second = sleep_before_second
        return self

    def set_button(self, button: str) -> "ActionComponent":
        self.button = button
        return self

    def set_retry_interval(self, retry_interval) -> "ActionComponent":
        self.retry_interval = retry_interval
        return self

    def set_timeout_second(self, timeout_second) -> "ActionComponent":
        self.timeout_second = timeout_second
        return self

    def set_confidence(self, confidence) -> "ActionComponent":
        self.confidence = confidence
        return self

    def set_timeout_func(self, func: Optional[Callable]) -> "ActionComponent":
        self.timeout_func = func
        return self

    def timeout_processing(self):
        Log.i("timeout")
        if self.timeout_func is not None:
            self.timeout_func()
            return
        if self.next is not None:
            self.next.exec()

    @abstractmethod
    def action(self) -> bool:
        pass

    def start(self):
        self.head.exec()

    def exec(self):
        start_time = time.time()
        time.sleep(self.sleep_before_second)    # 执行前等待
        while not self.action():
            if time.time() - start_time > self.timeout_second:
                self.timeout_processing()       # 超时处理
                return
            time.sleep(self.retry_interval)     # 重试间隔
        time.sleep(self.sleep_after_second)     # 执行后等待
        if self.next is not None:
            self.next.exec()


class NoneAction(ActionComponent):  # 空行为
    def __init__(self):
        super().__init__()

    def action(self) -> bool:
        return True

class ClickAction(ActionComponent):  # 点击窗口位置行为
    """
    Click behavior abstract class

    """

    def __init__(self, x: int = 0, y: int = 0, button="LEFT"):
        super().__init__(button=button)
        self.x = x
        self.y = y

    def action(self) -> bool:
        pyautogui.move(self.x, self.y, self.move_duration)
        pyautogui.click(button=self.button)
        return True

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": x:{}, y:{}".format(self.x, self.y))
        super(ClickAction, self).exec()


class ClickInsideWindowAction(ClickAction):  # 点击窗口内部位置行为
    def __init__(self, window: BaseWindow, x: int = 0, y: int = 0):
        super().__init__(x, y)
        self.window = window
        if self.window is not None:
            self.x = window.left + x
            self.y = window.top + y

    def action(self) -> bool:
        pyautogui.moveTo(self.x, self.y, duration=self.move_duration)
        pyautogui.click(button=self.button)
        return True

    def exec(self):
        if self.window is None:
            self.window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}".format(self.window, self.x, self.y))
        super(ClickInsideWindowAction, self).exec()


class ClickBasedOnWindowCenterAction(ClickAction):  # 相对窗口中心点击行为
    def __init__(self, window: BaseWindow, x: int = 0, y: int = 0, button="LEFT"):
        super().__init__(x, y, button=button)
        self.window = window
        if window is not None:
            center_x, center_y = WindowsUtil.get_window_center(window)
            self.x = center_x + x
            self.y = center_y + y

    def action(self) -> bool:
        pyautogui.moveTo(self.x, self.y, duration=self.move_duration)
        pyautogui.click(button=self.button)
        return True

    def exec(self):
        if self.window is None or not self.window.isActive:
            self.window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}".format(self.window, self.x, self.y))
        super(ClickBasedOnWindowCenterAction, self).exec()


class ImageClickAction(ClickAction):  # 点击图片行为
    def __init__(self, image: str, x: int = 0, y: int = 0, clicks: int = 1):
        super().__init__(x, y)
        self.image = ImageUtil.get_file(image)
        self.clicks = clicks
        if self.image is None:
            print(image + " not find")
        self.width, self.height = Image.open(self.image).size
        if x == 0:
            self.x = x
        else:
            self.x = x - self.width // 2
        if y == 0:
            self.y = y
        else:
            self.y = y - self.height // 2

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence)
        if location is not None:
            pyautogui.moveTo(location.x + self.x, location.y + self.y, self.move_duration)
            pyautogui.click(interval=0.1, duration=0.1, clicks=self.clicks, button=self.button)
            return True
        return False

    def exec(self):
        Log.e(str(self.__class__.__name__) + ": image:{}, x:{}, y:{}".
              format(self.image.split("\\")[-1], self.x, self.y))
        super(ImageClickAction, self).exec()


class AnyImageClickAction(ActionComponent):  # 任意图片点击行为
    def __init__(self, images: list):
        super().__init__()
        self.images = images

    def action(self) -> bool:
        for image in self.images:
            image_file = ImageUtil.get_file(image)
            if not os.path.exists(image_file):
                continue
            location = pyautogui.locateCenterOnScreen(image_file, confidence=self.confidence)
            if location is not None:
                pyautogui.moveTo(location.x, location.y, self.move_duration)
                pyautogui.click(location.x, location.y, clicks=1, interval=0.1, duration=0.1, button=self.button)
                return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": images:{}".format(self.images))
        super(AnyImageClickAction, self).exec()


class PriorImageClickActionComponent(ActionComponent):  # 优先级图片点击行为
    def __init__(self, images: list):
        super().__init__()
        self.images = images

    def action(self) -> bool:
        for image in self.images:
            location = pyautogui.locateCenterOnScreen(image, confidence=0.9)
            if location is not None:
                pyautogui.moveTo(location.x, location.y, self.move_duration)
                pyautogui.click(location.x, location.y, clicks=1, interval=0.1, duration=0.1, button="LEFT")
                return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": images:{}".format(self.images))
        super(PriorImageClickActionComponent, self).exec()


class MoveAction(ActionComponent):  # 给定窗口的相对位置点击行为
    def __init__(self, x=0, y=0):
        super().__init__()
        self.x = x
        self.y = y

    def action(self) -> bool:
        pyautogui.move(self.x, self.y, self.move_duration)
        return True

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": x:{}, y:{}".format(self.x, self.y))
        super(MoveAction, self).exec()


class MoveInsideWindowAction(MoveAction):
    def __init__(self, window: BaseWindow, x=0, y=0):
        super().__init__(x, y)
        self.window = window
        if window is not None:
            center_x, center_y = WindowsUtil.get_window_center(window)
            self.x = center_x + x
            self.y = center_y + y

    def action(self) -> bool:
        if self.window is not None:
            pyautogui.moveTo(self.x, self.y, self.move_duration)
            return True
        return False

    def exec(self):
        if self.window is None or not self.window.isActive:
            self.window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}".format(self.window, self.x, self.y))
        super(MoveInsideWindowAction, self).exec()


class RelativeLocationClickAction(ClickAction):  # 给定窗口的相对位置点击行为
    def __init__(self, window: BaseWindow, x, y):
        super().__init__()
        self.window = window
        if window is not None:
            self.x = window.top + window.width * x
            self.y = window.left + window.height * y

    def action(self) -> bool:
        pyautogui.moveTo(self.x, self.y, self.move_duration)
        pyautogui.click(self.x, self.y)
        return True

    def exec(self):
        if self.window is None or not self.window.isActive:
            self.window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}".format(self.window, self.x, self.y))
        super(RelativeLocationClickAction, self).exec()


class InputAction(ActionComponent):
    def __init__(self, input_content: str = ""):
        super().__init__()
        self.content = input_content

    def action(self) -> bool:
        pyautogui.typewrite(self.content)
        return True

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": content:{}".format(self.content))
        super(InputAction, self).exec()


class KeyAction(ActionComponent):
    def __init__(self, key: str, times2repeat: int = 1):
        super().__init__()
        self.key = key
        self.times2repeat = times2repeat

    def action(self) -> bool:
        for i in range(self.times2repeat):
            pyautogui.hotkey(self.key)
            time.sleep(0.1)
        return True

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": key:{}".format(self.key))
        super(KeyAction, self).exec()


class ImageAppearAction(ActionComponent):
    """
    图片出现行为
    """
    def __init__(self, image: str, timeout: int = 60):
        super().__init__()
        self.image = ImageUtil.get_file(image)
        self.timeout = timeout

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence)
        if location is not None:
            return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": image:{}, timeout:{}".format(self.image, self.timeout))
        super(ImageAppearAction, self).exec()

class ImageDisappearAction(ActionComponent):
    """
    图片消失行为
    """
    def __init__(self, image: str, timeout: int = 60 * 10):
        super().__init__()
        self.image = ImageUtil.get_file(image)
        self.timeout = timeout

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence)
        if location is None:
            return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": image:{}, timeout:{}".format(self.image, self.timeout))
        super(ImageDisappearAction, self).exec()


class RegionSelectionInsideWindowAction(ActionComponent):
    def __init__(self, window: BaseWindow, x, y, w, h):
        super().__init__()
        self.window = window
        if window is not None:
            self.x = self.window.left + x - w // 2
            self.y = self.window.top + y - h // 2
            self.w = w
            self.h = h

    def action(self) -> bool:
        if self.window is None:
            return False
        pyautogui.moveTo(self.x, self.y, self.move_duration)
        pyautogui.dragRel(self.w, self.h, self.move_duration, button="LEFT")
        return True

    def exec(self):
        if self.window is None or not self.window.isActive:
            self.window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}, w:{}, h:{}"
              .format(self.window, self.x, self.y, self.w, self.h))
        super(RegionSelectionInsideWindowAction, self).exec()


class FunctionAction(ActionComponent):
    def __init__(self, function: Callable):
        super().__init__()
        self.function = function

    def action(self) -> bool:
        return self.function()

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": function:{}".format(self.function))
        super(FunctionAction, self).exec()


if __name__ == "__main__":
    # WindowsUtil.instance.get_war3_window().activate()
    time.sleep(1)
    # ImageClickAction("5bo").start()

    AnyImageClickAction(["return2platform"]) \
        .set_retry_interval(1).set_timeout_second(.3) \
        .start()