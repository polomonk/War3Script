import sys
import time
from abc import ABC, abstractmethod
import WindowsUtil
from Action import *
from Strategy import Strategy


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

    def exec(self):
        self.strategy.in_platform()


class InRoomState(State):
    def __init__(self):
        super().__init__()

    def exec(self):
        self.strategy.in_room()


class InWar3State(State):
    def __init__(self):
        super().__init__()

    def exec(self):
        self.strategy.in_war3()


