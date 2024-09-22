from ..Tools.game import Game
from .actions import Dispatch
from abc import ABC, abstractmethod


class SimulatorAgent(ABC):
    def __init__(self, game: Game):
        self.game = game

    @abstractmethod
    def simulate(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def dispatch(self) -> Dispatch:
        pass

    @abstractmethod
    def simulate_current(self):
        pass

    @abstractmethod
    def reset_current(self):
        pass