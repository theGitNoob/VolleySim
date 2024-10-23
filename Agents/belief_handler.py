from abc import ABC, abstractmethod


class BeliefHandler(ABC):
    @abstractmethod
    def handle_belief(self, agent, key, value):
        pass
