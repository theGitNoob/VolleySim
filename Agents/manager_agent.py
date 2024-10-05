from Tools.line_up import LineUp

from .actions import Action
from .manager_action_strategy import ActionRandomStrategy, ManagerActionStrategy
from .manager_line_up_strategy import ManagerLineUpStrategy
from .simulator_agent import SimulatorAgent


class Manager:
    def __init__(
        self,
        line_up_strategy: ManagerLineUpStrategy,
        action_strategy: ManagerActionStrategy,
        team: str,
    ) -> None:
        self.line_up_strategy: ManagerLineUpStrategy = line_up_strategy
        self.action_strategy: ManagerActionStrategy = action_strategy
        self.team: str = team

    def get_line_up(self, simulator: SimulatorAgent) -> LineUp:
        return self.line_up_strategy.get_line_up(self.team, simulator)

    def action(self, simulator: SimulatorAgent) -> Action:
        return self.action_strategy.action(self.team, simulator)

    def heuristic_action(self, simulator: SimulatorAgent) -> Action:
        return ActionRandomStrategy().action(self.team, simulator)
