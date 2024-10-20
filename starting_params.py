from Agents.manager_action_strategy import (ActionRandomStrategy,
                                            ActionSimulateStrategy)
from Agents.manager_line_up_strategy import LineUpStandardStrategy
from Agents.player_strategy import MinimaxStrategy, VolleyballStrategy, RandomStrategy
from Simulator.simulation_params import SimulationParams


class StartingParams:
    def __init__(self, simulation_params, name: str):
        self.simulation_params = simulation_params
        self.name = name


team_names = ("USA", "JPN")

all_random = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionSimulateStrategy()),
        (VolleyballStrategy(), VolleyballStrategy()),
    ),
    "all_random",
)

all_smart = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionSimulateStrategy(), ActionSimulateStrategy()),
        (VolleyballStrategy(), VolleyballStrategy())
    ),
    'all_smart'
)
#
smart_line_up = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (RandomStrategy(), RandomStrategy())
    ),
    'smart_line_up'
)
#
smart_action = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionSimulateStrategy(), ActionSimulateStrategy()),
        (RandomStrategy(), RandomStrategy())
    ),
    'smart_action'
)

smart_vs_random_action = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionSimulateStrategy(), ActionRandomStrategy()),
        (RandomStrategy(), RandomStrategy())
    ),
    'smart_vs_random_action'
)

smart_player = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (VolleyballStrategy(), VolleyballStrategy())
    ),
    'smart_player'
)

smart_vs_random_player = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (VolleyballStrategy(), RandomStrategy())
    ),
    'smart_vs_random_player'
)

minimax_vs_random_player = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (MinimaxStrategy(), RandomStrategy())
    ),
    'minimax_vs_random_player'
)

minimax_vs_minimax_player = StartingParams(
    SimulationParams(
        team_names,
        (LineUpStandardStrategy(), LineUpStandardStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (MinimaxStrategy(), VolleyballStrategy()),
    ),
    "minimax_vs_minimax_player",
)
