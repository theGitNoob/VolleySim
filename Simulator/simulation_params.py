from typing import Tuple

from Agents.manager_action_strategy import ManagerActionStrategy
from Agents.manager_line_up_strategy import ManagerLineUpStrategy
from Agents.player_strategy import PlayerStrategy


class SimulationParams:
    def __init__(
        self,
        names: Tuple[str, str],
        managers_line_up: Tuple[ManagerLineUpStrategy, ManagerLineUpStrategy],
        managers_action_strategy: Tuple[ManagerActionStrategy, ManagerActionStrategy],
        players_action_strategy: Tuple[PlayerStrategy, PlayerStrategy],
    ) -> None:
        self.names: Tuple[str, str] = names
        self.managers_line_up: Tuple[ManagerLineUpStrategy, ManagerLineUpStrategy] = (
            managers_line_up
        )
        self.managers_action: Tuple[ManagerActionStrategy, ManagerActionStrategy] = (
            managers_action_strategy
        )
        self.players_action_strategy = players_action_strategy
