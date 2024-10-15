from abc import ABC, abstractmethod
from typing import List

from .actions import Action
from .behavior import Behavior


class Intention(ABC):
    @abstractmethod
    def select_action(self, behaviors: List[Behavior], game_state, possible_actions) -> Action:
        pass


class DefenseIntention(Intention):
    def select_action(self, behaviors, game_state, possible_actions) -> Action:
        return max(
            possible_actions,
            key=lambda a: sum([b.eval(a, game_state.game) for b in behaviors])
        )


class OffenseIntention(Intention):
    def select_action(self, behaviors, game_state, possible_actions) -> Action:
        return max(
            possible_actions,
            key=lambda a: sum([b.eval(a, game_state.game) for b in behaviors])
        )


class ReturnToPositionIntention(Intention):
    def select_action(self, behaviors, game_state, possible_actions) -> Action:
        return max(
            possible_actions,
            key=lambda a: sum([b.eval(a, game_state.game) for b in behaviors])
        )
