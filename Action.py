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

default_region = (0, 0, WindowsUtil.screen_width, WindowsUtil.screen_height)


class ActionComponent(ABC):
    """
    Behavior abstract class
    action(self) must implement
    timeout_processing(self) should implement
    """

    def __init__(self, sleep_after_second=0, button="LEFT", move_duration=0.1, retry_interval=0.5):
        super().__init__()
        self.success_callback: Optional[Callable] = None
        self.head: ActionComponent = self  # 头节点
        self.next: Optional[ActionComponent, None] = None  # 下一个节点
        self.sleep_before_second: int = 0  # 执行前等待时间
        self.sleep_after_second: float = sleep_after_second  # 执行后等待时间
        self.button = button  # 鼠标按键
        self.move_duration = move_duration  # 鼠标移动时间
        # 异常处理
        self.retry_interval = retry_interval  # 重试间隔
        self.timeout_second = 1  # 超时时间
        self.confidence = 0.8  # 图片置信度
        self.timeout_func: Optional[Callable] = None  # 超时处理函数

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

    def set_success_func(self, func: Callable) -> "ActionComponent":
        self.success_callback = func
        return self

    def set_timeout_func(self, func: Optional[Callable]) -> "ActionComponent":
        self.timeout_func = func
        return self

    @abstractmethod
    def action(self) -> bool:
        pass

    def start(self):
        self.head.exec()

    def exec(self):
        start_time = time.time()
        time.sleep(self.sleep_before_second)  # 执行前等待
        is_succeeded = self.action()
        while not is_succeeded:
            if time.time() - start_time > self.timeout_second:  # 超时处理
                Log.i("timeout")
                if self.timeout_func is not None:   # 执行超时处理函数
                    self.timeout_func()
                    return
                break
            if self.timeout_second != 0:
                time.sleep(self.retry_interval)  # 重试间隔
                is_succeeded = self.action()
        if time.time() - start_time <= self.timeout_second:     # 执行成功回调
            if self.success_callback is not None:
                self.success_callback()
        time.sleep(self.sleep_after_second)  # 执行后等待
        if self.next is not None:
            self.next.exec()


class NoneAction(ActionComponent):  # 空行为
    def __init__(self):
        super().__init__()

    def action(self) -> bool:
        return True


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


class ClickAction(ActionComponent):  # 点击行为
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
        super().exec()


class ImageClickAction(ClickAction):  # 点击图片行为
    def __init__(self, image_path: str, x: int = 0, y: int = 0, clicks: int = 1,
                 region=default_region):
        super().__init__(x, y)
        self.image_path = image_path
        self.image = ImageUtil.get_file(image_path)
        self.clicks = clicks
        self.region = region
        if self.image is None:
            Log.e(image_path + " not find")
        self.width, self.height = self.image.size
        if x == 0:
            self.x = x
        else:
            self.x = x - self.width // 2
        if y == 0:
            self.y = y
        else:
            self.y = y - self.height // 2

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence, region=self.region)
        if location is not None:
            pyautogui.moveTo(location.x + self.x, location.y + self.y, self.move_duration)
            pyautogui.click(interval=0.1, duration=0.1, clicks=self.clicks, button=self.button)
            return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": image:{}, x:{}, y:{}".
              format(self.image_path.split("\\")[-1], self.x, self.y))
        super().exec()

    def set_region(self, region):
        self.region = region


class AnyImageClickAction(ActionComponent):  # 任意图片点击行为
    def __init__(self, images_path: list[str], region=(0, 0, WindowsUtil.screen_width, WindowsUtil.screen_height)):
        super().__init__()
        self.images_path = images_path
        self.region = region

    def action(self) -> bool:
        for image_path in self.images_path:
            image = ImageUtil.get_file(image_path)
            location = pyautogui.locateCenterOnScreen(image, confidence=self.confidence, region=self.region)
            if location is not None:
                pyautogui.moveTo(location.x, location.y, self.move_duration)
                pyautogui.click(location.x, location.y, clicks=1, interval=0.1, duration=0.1, button=self.button)
                return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": images:{}".format(*self.images_path))
        super(AnyImageClickAction, self).exec()

    def set_region(self, region):
        self.region = region


class ImageAppearAction(ActionComponent):
    """
    图片出现行为
    """

    def __init__(self, image_path: str, timeout: int = 60, region=(0, 0, WindowsUtil.screen_width, WindowsUtil.screen_height)):
        super().__init__()
        self.image_path = image_path
        self.image = ImageUtil.get_file(image_path)
        self.region = region
        self.timeout = timeout
        self.after_click_image_path: Optional[str] = None

    def set_after_click_image(self, image_path: str):
        self.after_click_image_path = image_path
        return self

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence, region=self.region)
        if location is not None:
            if self.after_click_image_path is not None:
                detail_region = (location.x - self.image.width // 2, location.y - self.image.height // 2,
                                 location.x + self.image.width // 2, location.y + self.image.height // 2)
                ImageClickAction(self.after_click_image_path, region=detail_region)\
                    .set_confidence(0.7)\
                    .set_timeout_second(0)\
                    .exec()
            return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": image:{}, timeout:{}".format(self.image_path, self.timeout))
        super().exec()

    def set_region(self, region):
        self.region = region


class ImageDisappearAction(ActionComponent):
    """
    图片消失行为
    """

    def __init__(self, image_path: str, timeout: int = 60 * 10, region=(0, 0, WindowsUtil.screen_width, WindowsUtil.screen_height)):
        super().__init__()
        self.image_path = image_path
        self.image = ImageUtil.get_file(image_path)
        self.region = region
        self.timeout = timeout

    def action(self) -> bool:
        location = pyautogui.locateCenterOnScreen(self.image, confidence=self.confidence, region=self.region)
        if location is None:
            return True
        return False

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": image:{}, timeout:{}".format(self.image_path, self.timeout))
        super(ImageDisappearAction, self).exec()

    def set_region(self, region):
        self.region = region


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


class FunctionAction(ActionComponent):
    def __init__(self, function: Callable):
        super().__init__()
        self.function = function

    def action(self) -> bool:
        return self.function()

    def exec(self):
        Log.d(str(self.__class__.__name__) + ": function:{}".format(self.function))
        super(FunctionAction, self).exec()


class WindowAction(ActionComponent, ABC):
    def __init__(self, app_window: BaseWindow, x: int = 0, y: int = 0):
        super().__init__()
        self.app_window = app_window
        self.x = x
        self.y = y
        if self.app_window is not None:
            self.x += self.app_window.left
            self.y += self.app_window.top

    @abstractmethod
    def action(self) -> bool:
        pass

    def exec(self):
        if self.app_window is None or self.app_window.isMinimized or not self.app_window.isActive:
            self.app_window = None
        Log.d(str(self.__class__.__name__) + ": window:{}, x:{}, y:{}".format(self.app_window, self.x, self.y))
        super().exec()

    def is_window_available(self):
        return not (self.app_window is None or self.app_window.isMinimized or not self.app_window.isActive)


class ClickWindowAction(WindowAction):  # 点击窗口内部位置行为
    def __init__(self, app_window: BaseWindow, x: int = 0, y: int = 0):
        super().__init__(app_window, x, y)

    def action(self) -> bool:
        if not self.is_window_available():
            return False
        pyautogui.moveTo(self.x, self.y, duration=self.move_duration)
        pyautogui.click(button=self.button)
        return True

    def exec(self):
        super().exec()


class CenterClickWindowAction(WindowAction):  # 相对窗口中心点击行为
    def __init__(self, app_window: BaseWindow, offset_x: int = 0, offset_y: int = 0, button: str = "LEFT"):
        super().__init__(app_window)
        self.button = button
        if self.is_window_available():
            center_x, center_y = self.app_window.left + self.app_window.width // 2, self.app_window.top + self.app_window.height // 2
            self.x += center_x
            self.y += center_y

    def action(self) -> bool:
        if not self.is_window_available():
            return False
        pyautogui.moveTo(self.x, self.y, duration=self.move_duration)
        pyautogui.click(button=self.button)
        return True

    def exec(self):
        super().exec()


class CenterMoveWindowAction(WindowAction):
    def __init__(self, app_window: BaseWindow, x=0, y=0):
        super().__init__(app_window, x, y)
        if self.is_window_available():
            center_x, center_y = self.app_window.left + self.app_window.width // 2, self.app_window.top + self.app_window.height // 2
            self.x += center_x
            self.y += center_y

    def action(self) -> bool:
        if not self.is_window_available():
            return False
        pyautogui.moveTo(self.x, self.y, self.move_duration)
        return True

    def exec(self):
        super().exec()


class RegionSelectionWindowAction(WindowAction):
    def __init__(self, app_window: BaseWindow, x, y, region_width=50, region_height=50):
        super().__init__(app_window, x, y)
        self.region_width = region_width
        self.region_height = region_height
        if self.is_window_available():
            self.x += self.app_window.left - self.region_width // 2
            self.y += self.app_window.top - self.region_height // 2

    def action(self) -> bool:
        if not self.is_window_available():
            return False
        pyautogui.moveTo(self.x, self.y, self.move_duration)
        pyautogui.dragRel(self.region_width, self.region_height, self.move_duration, button="LEFT")
        return True

    def exec(self):
        super().exec()


if __name__ == "__main__":
    window = WindowsUtil.instance.get_war3_window()
    if window is not None and not window.isMinimized:
        window.activate()
    print(window.isMinimized)
