from abc import ABC, abstractmethod

from Agents.actions import Action


class IntentionHandler(ABC):
    def __init__(self, intention_name: str):
        self.intention_name = intention_name

    @abstractmethod
    def get_action(self, agent) -> Action:
        pass
