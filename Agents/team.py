from typing import Dict

from .actions import Action
from .manager_agent import Manager
from .player_agent import Player
from .simulator_agent import SimulatorAgent


class TeamAgent:
    def __init__(self, name: str, manager: Manager, players: Dict[int, Player]) -> None:
        self.name = name
        self.manager: Manager = manager
        self.players: Dict[int, Player] = players

    def play(self, simulator: SimulatorAgent) -> Action:
        return self.manager.action(simulator=simulator)
