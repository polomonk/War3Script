from State import *
from Strategy import HangUpStrategy, CarryStrategy, WeaponSoulStrategy


# 创建房间 -> 等待开始 -> 选英雄->f7->移动到冥想位置->冥想->结束->关闭魔兽->准备
def init_state():
    if WindowsUtil.instance.get_war3_window() is not None:
        # inside war3
        return InWar3State()
    elif WindowsUtil.instance.get_platform_window() is not None:
        if len(pyautogui.getWindowsWithTitle(WindowsUtil.platform_window_title)) > 1:
            # inside room
            return InRoomState()
        else:
            # inside platform
            return InPlatformState()
    else:
        # open platform
        pass


def platform_restore():
    platform_window = window_util.get_platform_window()
    if platform_window is None:
        WindowsUtil.open_platform()
    platform_window.restore()
    if platform_window.isMaximized:  # nom -> max -> min : reverse
        platform_window.restore()
    platform_window.activate()


def main():
    state = init_state()
    strategy = WeaponSoulStrategy()
    strategy.set_model("nModel").set_difficulty(1)  # 军团降临, 难度一
    state.set_strategy(strategy)
    state.exec()


window_util = WindowsUtil.instance


if __name__ == '__main__':
    while True:
        # try:
        main()
        # except Exception as e:
        #     print(e)

