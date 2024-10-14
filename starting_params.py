from Agents.manager_action_strategy import ActionRandomStrategy, ActionSimulateStrategy
from Agents.manager_line_up_strategy import LineUpRandomStrategy
from Agents.player_strategy import VolleyballStrategy, MinimaxStrategy
from Simulator.simulation_params import SimulationParams


class StartingParams:
    def __init__(self, simulation_params, name: str):
        self.simulation_params = simulation_params
        self.name = name


# Nombres de equipos de voleibol (puedes reemplazarlos por los que prefieras)
team_names = ("CUB", "JPN")

# Configuraciones de inicio para diferentes escenarios de simulación
all_random = StartingParams(
    SimulationParams(
        team_names,
        (LineUpRandomStrategy(), LineUpRandomStrategy()),
        (ActionRandomStrategy(), ActionSimulateStrategy()),
        (VolleyballStrategy(), VolleyballStrategy()),
    ),
    "all_random",
)

# all_smart = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpFixedStrategy(), LineUpFixedStrategy()),
#         (ActionSimulateStrategy(), ActionSimulateStrategy()),
#         (VolleyballStrategy(), VolleyballStrategy())
#     ),
#     'all_smart'
# )
#
# smart_line_up = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpFixedStrategy(), LineUpFixedStrategy()),
#         (ActionRandomStrategy(), ActionRandomStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'smart_line_up'
# )
#
# smart_vs_random_line_up = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpFixedStrategy(), LineUpRandomStrategy()),
#         (ActionRandomStrategy(), ActionRandomStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'smart_vs_random_line_up'
# )
#
# smart_action = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionSimulateStrategy(), ActionSimulateStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'smart_action'
# )
#
# smart_vs_random_action = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionSimulateStrategy(), ActionRandomStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'smart_vs_random_action'
# )
#
# minimax_vs_minimax_action = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionMiniMaxStrategy(), ActionMiniMaxStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'minimax_vs_minimax_action'
# )
#
# minimax_vs_random_action = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionMiniMaxStrategy(), ActionRandomStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'minimax_vs_random_action'
# )
#
# minimax_vs_smart_action = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionMiniMaxStrategy(), ActionSimulateStrategy()),
#         (RandomStrategy(), RandomStrategy())
#     ),
#     'minimax_vs_smart_action'
# )
#
# smart_player = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionRandomStrategy(), ActionRandomStrategy()),
#         (VolleyballStrategy(), VolleyballStrategy())
#     ),
#     'smart_player'
# )
#
# smart_vs_random_player = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionRandomStrategy(), ActionRandomStrategy()),
#         (VolleyballStrategy(), RandomStrategy())
#     ),
#     'smart_vs_random_player'
# )
#
# minimax_vs_random_player = StartingParams(
#     SimulationParams(
#         team_names,
#         (LineUpRandomStrategy(), LineUpRandomStrategy()),
#         (ActionRandomStrategy(), ActionRandomStrategy()),
#         (MinimaxStrategy(), RandomStrategy())
#     ),
#     'minimax_vs_random_player'
# )
#
minimax_vs_minimax_player = StartingParams(
    SimulationParams(
        team_names,
        (LineUpRandomStrategy(), LineUpRandomStrategy()),
        (ActionRandomStrategy(), ActionRandomStrategy()),
        (MinimaxStrategy(), VolleyballStrategy())
    ),
    'minimax_vs_minimax_player'
)
