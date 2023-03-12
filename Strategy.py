import math
import random
import time
import difflib
import pyautogui
from pytesseract import pytesseract

import OCR
import WindowsUtil
from Action import *
from Action import ActionComponent
import Hero

game_failed = "游戏失败"
attack_warning = "警告:时空枢纽的剩余生命值"


class Strategy(ABC):
    def __init__(self):
        super().__init__()
        self.model = "nModel"
        self.difficulty = 1
        self.opened_weapon_soul = False

    @abstractmethod
    def create_room(self):
        pass

    def wait_to_start(self):  # 等待游戏开始
        ImageDisappearAction("noPerson") \
            .set_next_action(AnyImageClickAction(["ready", "startGame"])) \
            .start()

    def set_model(self, model: str):
        self.model = model
        return self

    def set_difficulty(self, difficulty: int):
        self.difficulty = difficulty
        return self

    def select_model_and_difficulty(self):
        # 选择模式  nModel, kModel
        # 选择难度  1-5(500, 302 + 70*(n-1)) 6-10(740, 302 + 70*(n-1) # 难度图标(192 , 80)  (608, 294)
        x = 500 + 192 // 2 if self.difficulty <= 5 else 740 + 192 // 2
        y = 294 + (self.difficulty - 1) * 70
        ImageClickAction(self.model + "Text").set_confidence(0.7).set_after_second(1) \
            .set_next_action(ClickInsideWindowAction(WindowsUtil.instance.get_war3_window(), x, y)) \
            .start()

    def choose_hero(self):
        ImageClickAction("heroBottom").set_confidence(0.6).set_timeout_second(3).set_after_second(1) \
            .start()
        return True

    def init_war3window(self):
        if not Hero.instance.get_state():  # 没有英雄属性界面说明还在加载界面
            self.select_model_and_difficulty()
            self.choose_hero()
            # self.share_sharing()
        ImageClickAction("noticeBoard", 466, 32) \
            .start()
        # for i in range(15):
        #     time.sleep(.05)
        #     pyautogui.scroll(-1000)

    def share_sharing(self):
        # 共享物品和角色
        ImageClickAction("setup") \
            .set_next_action(ImageClickAction("itemSharing", 90)).set_timeout_second(.5).set_confidence(0.98) \
            .set_next_action(KeyAction("F11")) \
            .set_next_action(ImageClickAction("teamSharing", 150, 15)).set_timeout_second(0).set_confidence(0.95) \
            .set_next_action(ImageClickAction("teamSharing", 150, 15)).set_timeout_second(0).set_confidence(0.95) \
            .set_next_action(ImageClickAction("teamSharing", 150, 15)).set_timeout_second(0).set_confidence(0.95) \
            .set_next_action(ImageClickAction("accept")).set_confidence(0.8).set_timeout_second(1) \
            .set_next_action(KeyAction("Esc")).start()

    def transformation(self):
        # 等待其他玩家输入变身后输入变身
        ImageClickAction("transformation").set_timeout_second(60 * 60 * 1).set_confidence(0.7) \
            .set_next_action(KeyAction("Enter")) \
            .set_next_action(InputAction("bianshen")) \
            .set_next_action(KeyAction("Space")) \
            .set_next_action(KeyAction("Enter")) \
            .start()

    def meditation(self):  # 冥想
        window = WindowsUtil.instance.get_war3_window()
        if window is not None and not window.isMinimized:
            window.activate()
            Hero.instance.meditation()

    def weapon_soul(self):
        def weapon_soul_opened():
            self.opened_weapon_soul = True

        # 器灵(631, 271), 物品栏第一行,第一列(942, 780)
        KeyAction("F2").set_next_action(
            RegionSelectionInsideWindowAction(WindowsUtil.instance.get_war3_window(), 631, 271)) \
            .set_next_action(ClickBasedOnWindowCenterAction(WindowsUtil.instance.get_war3_window(), button="RIGHT")) \
            .set_next_action(ImageClickAction("weaponSoul", 0, 0)).set_confidence(0.7) \
            .set_success_func(weapon_soul_opened) \
            .start()

    def exit_game(self):
        window = WindowsUtil.instance.get_war3_window()
        if window is None:
            return
        if window.isMinimized:
            window.restore()
            window.activate()
        KeyAction("f10") \
            .set_next_action(KeyAction("e")) \
            .set_next_action(KeyAction("x")) \
            .set_next_action(KeyAction("x")) \
            .start()

    """
    createRoom -> waitForStart (-> selectModel -> selectDifficult) -> selectHero -> f7 -> move -> meditation 
        -> waitForGameOver -> exit -> return2platform
    """

    @abstractmethod
    def in_platform(self):
        pass

    @abstractmethod
    def in_room(self):
        pass

    def in_war3(self):
        if WindowsUtil.instance.get_war3_window() is None:
            time.sleep(1)
            return
        self.init_war3window()


class WeaponSoulStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.needBackToBase = False
        self.war3_inited = False

    def search_room(self):
        # 搜索房间. 相对窗口库左上角位置:搜索(360, 440), 搜索(360, 440)
        ImageClickAction("meditation", clicks=2) \
            .start()

    def create_room(self):
        ImageClickAction("createRoom").set_confidence(0.7).set_after_second(1) \
            .set_next_action(ImageClickAction("roomPassword", 145)) \
            .set_next_action(InputAction("123")) \
            .set_next_action(ImageClickAction("create")) \
            .start()

    def in_platform(self):
        ImageClickAction("sure").action()
        self.create_room()

    def in_room(self):
        ImageClickAction("sure").action()
        AnyImageClickAction(["startGame", "ready"]) \
            .start()

    def in_war3(self):
        # super(HangUpStrategy, self).in_war3()
        start_time = time.time()
        while True:
            if WindowsUtil.instance.get_war3_window() is None:  # 退出游戏
                return
            elif AnyImageClickAction(["return2platform"]).action():
                return
            elif (time.time() - start_time) > 60 * 60 * 1:
                self.exit_game()
                return
            if not self.war3_inited:  # 进入了魔兽界面
                self.select_model_and_difficulty()
                if ImageAppearAction("setup").action():
                    self.war3_inited = True
                    self.choose_hero()
                    ImageClickAction("noticeBoard", 466, 32) \
                        .start()
                    ImageClickAction("weaponPassiveSkills").set_confidence(0.7).action()
                    self.meditation()
                    self.share_sharing()
                    # 镜头拉倒最远
                    for i in range(15):
                        time.sleep(.05)
                        pyautogui.scroll(-1000)
            # lines = OCR.get_system_message(4)
            # for line in lines:
            #     if line is None or line == "":
            #         continue
            #     if OCR.is_text_left_match(line, attack_warning):
            #         KeyAction("F2").start()
            #     elif OCR.is_text_left_match(line, game_failed):
            #         self.exit_game()
            #     elif self.opened_weapon_soul:
            #         expected = "【项灵图鉴]玩家<" + Hero.instance.name + ">获得了一个品灵图监"
            #         if OCR.is_text_left_match(line, expected):
            #             self.exit_game()
            #             return
            # 等待15波怪物 (658, 47, 685, 85) 回基地防守
            if ImageAppearAction("wave15").set_confidence(0.96).action():
                window = WindowsUtil.instance.get_war3_window()
                if window is not None and not window.isMinimized:
                    window.activate()
                self.needBackToBase = True
                KeyAction("F2").start()
            if not self.opened_weapon_soul and ImageAppearAction("over").set_confidence(0.95).action():
                self.weapon_soul()

                # 军团(620, 50, 35, 20)
            time.sleep(5)


class CarryStrategy(Strategy):
    """
    carry strategy
    """

    def create_room(self):
        # 创建房间. 相对窗口库左上角位置:房间名称(350 124), 地图等级spinner(300, 265), editView(420, 265), 创建(360, 440)
        ImageClickAction("createRoom").set_confidence(0.7).set_after_second(0.5) \
            .set_next_action(ImageClickAction("roomPassword", 145)) \
            .set_next_action(InputAction("123")) \
            .set_next_action(ImageClickAction("create")) \
            .start()

    def in_platform(self):
        self.create_room()
        # self.wait_to_start()

    def in_room(self):
        AnyImageClickAction(["ready", "startGame"]) \
            .start()

    def in_war3(self):
        super(CarryStrategy, self).in_war3()
        # self.exit_game()


class HangUpStrategy(Strategy):
    """
    hang up strategy

    springFestivalGift(635, 335), goods(520, 450), mysteryGift(720, 350)
    domainOfShadows(330, 230), attributeCultivation(480, 260), resourceStore(635, 255), endlessTower(790, 260)
    runeShop(350, 350), runeCopy(350, 470), killsShop(335, 580), 
    heroicBreakthrough(915, 355), skilledShops(935, 460), raffleShop(945, 585)
    """

    def main_line(self):
        pass

    def carry(self):
        pass


if __name__ == '__main__':
    window = WindowsUtil.instance.get_war3_window()
    if window is not None:
        window.activate()
    strategy = WeaponSoulStrategy()
    # strategy.in_platform()
    # strategy.in_room()
    # strategy.in_war3()
    # Hero.instance.get_state()
    while True:
        lines = OCR.get_system_message(4)
        for line in lines:
            if line is None or line == "":
                continue
            if OCR.is_text_left_match(line, attack_warning):
                pass
            elif OCR.is_text_left_match(line, game_failed):
                pass
        time.sleep(1)
