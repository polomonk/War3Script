import OCR
import WindowsUtil
from Action import *


# 从OCR识别出来的字符串中解析
def parse_main_line(main_line: str) -> str:
    if main_line.isdigit():  # 主线
        return main_line[0] + "-" + main_line[1:]
    else:
        return main_line.replace(".", "-")


def parse_red_equip(red_equip: str) -> str:
    if red_equip.isdigit():
        return red_equip[0] + "/" + red_equip[1:]
    else:
        return red_equip.replace("I", "/")


def parse_practice(practice: str) -> str:
    if practice.isdigit():
        return practice[0] + "-" + practice[1:]
    else:
        return practice.replace(".", "-")


class Hero:
    def __init__(self, name: str = "", hero_type: int = 0):
        self.owner = "polomonk"
        # self.owner = "MistakerOB"
        self.name = name
        self.type = hero_type  # 0:物理, 1:攻击, 2:法师
        self.power = "0"
        self.main_line = "0-0"
        self.red_equip = "0/0"
        self.tower_level = 0
        self.practice = "0-0"
        self.game_state = "正在游戏"
        self.app_window = None

    def __str__(self):
        return self.owner + "  战力:" + self.power + "  主线:" + self.main_line + "  吞噬红装:" + self.red_equip + \
               "  无尽之塔:" + str(self.tower_level) + "  属性修炼:" + self.practice + "  游戏状态:" + self.game_state

    @property
    def is_window_available(self):
        self.app_window = WindowsUtil.instance.get_war3_window()
        return self.app_window is not None and not self.app_window.isMinimized

    def focus_hero(self):
        if not self.is_window_available:
            return
        KeyAction("F1").set_after_second(0.01) \
            .set_next_action(KeyAction("F1")) \
            .start()

    def move(self, x, y):
        if not self.is_window_available:
            return
        self.focus_hero()
        CenterClickWindowAction(self.app_window, x, y).set_button("RIGHT") \
            .start()

    def jump(self, x, y, dumps=1):
        if not self.is_window_available:
            return
        self.focus_hero()
        x = min(window.width // 2, x)
        y = min(window.height // 2, y)
        action = CenterMoveWindowAction(window, x, y)
        for i in range(dumps):
            action = action.set_next_action(InputAction("d"))
        action.start()

    def jump_to_left(self, dumps=1):
        self.jump(WindowsUtil.screen_width, 0, dumps)

    def jump_to_right(self, dumps=1):
        self.jump(-WindowsUtil.screen_width, 0, dumps)

    def jump_to_top(self, dumps=1):
        self.jump(0, -WindowsUtil.screen_height, dumps)

    def jump_to_bottom(self, dumps=1):
        self.jump(0, WindowsUtil.screen_height, dumps)

    def back_to_base(self):
        if not self.is_window_available:
            return
        KeyAction("F2") \
            .start()

    def back_to_training_room(self):
        if self.is_window_available:
            return
        KeyAction("F3") \
            .start()

    def meditation(self):
        if not self.is_window_available:
            return
        app_window = WindowsUtil.instance.get_war3_window()
        KeyAction("f7") \
            .set_next_action(ClickWindowAction(app_window, app_window.width // 2, (app_window.height // 2) - 100)) \
            .set_button("RIGHT") \
            .set_next_action(ImageClickAction("askForAdvice")).set_retry_interval(0.05) \
            .start()

    def main_line(self):
        if not self.is_window_available:
            return
        # todo 增加主线功能
        InputAction("c") \
            .set_timeout_second(5).set_timeout_func(KeyAction("F2").action) \
            .start()

    def get_state(self) -> bool:
        if not self.is_window_available:
            return False
        for i in range(0, 4):
            line = OCR.region_text(window.left + 928, window.top + 160 + 25 * i, 340, 25).__str__()
            # 0.玩家(，)战斗力, 1.主线， 2.吞噬装备， 3.无尽之塔， 4.属性修炼, 5.游戏状态
            if OCR.is_text_match(self.owner, line[:len(self.owner) + 1]):
                info = line.split()
                if len(info) == 6:
                    self.power = info[0]
                elif len(info) == 7:
                    self.power = info[1]
                    info = info[1:]
                else:
                    Log.e(line + " line size is:" + str(len(info)))
                    return False
                self.main_line = parse_main_line(info[1])
                self.red_equip = parse_red_equip(info[2])
                self.tower_level = info[3]
                self.practice = parse_practice(info[4])
                self.game_state = info[5] + "戏"
                return True
        return False


instance = Hero()

if __name__ == '__main__':
    window = WindowsUtil.instance.get_war3_window()
    if window is not None:
        window.activate()
        instance.jumpToLeft()
    # while True:
        # print(instance.get_state())
        # time.sleep(1)
