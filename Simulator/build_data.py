from typing import List

from pandas import DataFrame

from Agents.manager_agent import Manager
from Agents.player_agent import Player
from Agents.team import TeamAgent
from Simulator.simulation_params import SimulationParams
from Simulator.simulator import VolleyballSimulation
from Tools.data import PlayerData, TeamData
from Tools.enum import T1, T2


def get_data(team: str, df: DataFrame) -> List[PlayerData]:
    data = df[df["Team"] == team]
    return [PlayerData(p) for _, p in data.iterrows()]


def conf_game(params: SimulationParams, df: DataFrame) -> VolleyballSimulation:
    T1_n, T2_n = params.names
    t1_line_up, t2_line_up = params.managers_line_up
    T1_action, T2_action = params.managers_action
    T1_player, T2_player = params.players_action_strategy

    T1_players = get_data(T1_n, df)
    T2_players = get_data(T2_n, df)

    T1_data = TeamData(T1_n, T1_players)
    T2_data = TeamData(T2_n, T2_players)

    T1_players_agents = {
        player.dorsal: Player(player.dorsal, T1, T1_player) for player in T1_players
    }
    T2_players_agents = {
        player.dorsal: Player(player.dorsal, T2, T2_player) for player in T2_players
    }

    T1_manager = Manager(t1_line_up, T1_action, T1)
    T2_manager = Manager(t2_line_up, T2_action, T2)

    T1_team_agent = TeamAgent(T1_n, T1_manager, T1_players_agents)
    T2_team_agent = TeamAgent(T2_n, T2_manager, T2_players_agents)

    simulation = VolleyballSimulation(
        (T1_team_agent, T1_data), (T2_team_agent, T2_data)
    )

    return simulation
