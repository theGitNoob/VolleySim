# desire_handler.py

from abc import ABC, abstractmethod


class DesireHandler(ABC):
    def __init__(self, desire_name: str):
        self.desire_name = desire_name

    @abstractmethod
    def generate_desires(self, agent):
        pass
