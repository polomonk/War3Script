import ORC
import WindowsUtil
from Action import *


# 从ORC识别出来的字符串中解析
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
        self.name = name
        self.type = hero_type  # 0:物理, 1:攻击, 2:法师
        self.power = "0"
        self.main_line = "0-0"
        self.red_equip = "0/0"
        self.tower_level = 0
        self.practice = "0-0"
        self.game_state = "正在游戏"

    def __str__(self):
        return self.owner + "  战力:" + self.power + "  主线:" + self.main_line + "  吞噬红装:" + self.red_equip + \
               "  无尽之塔:" + str(self.tower_level) + "  属性修炼:" + self.practice + "  游戏状态:" + self.game_state

    def select_hero(self):
        KeyAction("F1").set_after_second(0.01) \
            .set_next_action(KeyAction("F1")) \
            .start()

    def move(self, x, y):
        window = WindowsUtil.instance.get_war3_window()
        self.select_hero()
        ClickBasedOnWindowCenterAction(window, x, y).set_button("RIGHT") \
            .start()

    def dump(self, x, y, dumps=1):
        window = WindowsUtil.instance.get_war3_window()
        print(window)
        center_x, center_y = WindowsUtil.get_window_center(window)
        print(x, y)
        print(center_x, center_y)
        x, y = min(center_x + x, window.width // 2 - 100), min(center_y + y, window.height // 2 - 100)  # 不超过窗口
        print(x, y)
        self.select_hero()
        action = MoveInsideWindowAction(window, x, y)
        for i in range(dumps):
            action.set_next_action(InputAction("d"))
        action.start()

    def get_state(self) -> bool:
        window = WindowsUtil.instance.get_war3_window()
        for i in range(1, 5):
            line = ORC.region_text(window.left + 928, window.top + 160 + 25 * i, 340, 25).__str__()
            Log.d(line)
            # 0.玩家(，)战斗力, 1.主线， 2.吞噬装备， 3.无尽之塔， 4.属性修炼, 5.游戏状态
            if ORC.is_string_match(self.owner, line[:len(self.owner) + 1]):
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
    while True:
        instance.get_state()
        print(instance)
        time.sleep(1)
