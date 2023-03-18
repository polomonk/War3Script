import sys
import time
from abc import ABC, abstractmethod
from Action import *
from Strategy import Strategy


# 傻逼墙(598, 23)
def close_kk_wall():
    ImageClickAction("kkWall", 598, 23).set_timeout_second(0.1).set_confidence(0.8).start()


class State(ABC):
    def __init__(self):
        self.next_state: Optional["State", None] = None
        self.strategy: Optional["Strategy", None] = None

    def set_next_state(self, next_state: "State") -> "State":
        self.next_state = next_state
        next_state.strategy = self.strategy
        return self.next_state

    def set_strategy(self, strategy: "Strategy") -> "State":
        self.strategy = strategy
        return self

    @abstractmethod
    def exec(self):
        pass


class InPlatformState(State):
    def __init__(self):
        super().__init__()
        Log.i("InPlatformState")

    def exec(self):
        super(InPlatformState, self).exec()
        app_window = WindowsUtil.instance.get_platform_window()
        if app_window is not None and not app_window.isMinimized:
            app_window.activate()
            close_kk_wall()
        self.strategy.in_platform()


class InRoomState(State):
    def __init__(self):
        super().__init__()
        Log.i("InRoomState")

    def exec(self):
        super(InRoomState, self).exec()
        app_window = WindowsUtil.instance.get_platform_room_window()
        if app_window is not None and not app_window.isMinimized:
            app_window.activate()
            close_kk_wall()
        self.strategy.in_room()


class InWar3State(State):
    def __init__(self):
        super().__init__()
        Log.i("InWar3State")

    def exec(self):
        app_window = WindowsUtil.instance.get_war3_window()
        if app_window is not None and not app_window.isMinimized:
            app_window.activate()
        super(InWar3State, self).exec()
        self.strategy.in_war3()


if __name__ == '__main__':
    # 打印时间日期
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    Log.i(time.strftime("%Y-%m-%d %H:%M:%S".format(time.localtime()) + "  InWar3State"))

