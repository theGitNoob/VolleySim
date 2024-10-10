from typing import Dict

from .manager_agent import Manager
from .player_agent import Player


class TeamAgent:
    def __init__(self, name: str, manager: Manager, players: Dict[int, Player]) -> None:
        self.name = name
        self.manager: Manager = manager
        self.players: Dict[int, Player] = players

    def select_next_player(self):
        return self.manager.get_line_up().next_player()
