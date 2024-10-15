from typing import Dict, List, Set, Tuple

from .line_up import LineUp
from .player_data import PlayerData


class PlayerStatistics:

    def __init__(self):
        self.points: int = 0
        self.attacks: int = 0
        self.errors: int = 0
        self.blocks: int = 0
        self.aces: int = 0
        self.digs: int = 0
        self.receives: int = 0
        self.serves: int = 0
        self.sets: int = 0

        self.total_attacks: int = 0
        self.total_blocks: int = 0
        self.total_aces: int = 0
        self.total_digs: int = 0
        self.total_receives: int = 0
        self.total_serves: int = 0
        self.total_sets: int = 0
        self.total_points: int = 0


class TeamStatistics:

    def __init__(self, team_name: str):
        self.team_name: str = team_name

        self.points: int = 0
        self.aces: int = 0
        self.errors: int = 0
        self.blocks: int = 0
        self.digs: int = 0
        self.attacks: int = 0
        self.substitutions: int = 0
        self.serves: int = 0
        self.sets_won: int = 0
        self.sets_lost: int = 0
        self.receives: int = 0
        self.sets: int = 0


class TeamData:

    def __init__(self, name: str, players: List[PlayerData]) -> None:
        self.name = name
        self.line_up: None | LineUp = None
        self.data: Dict[int, PlayerData] = {}
        self.statistics: TeamStatistics = TeamStatistics(name)
        self.players_statistics: Dict[int, PlayerStatistics] = {}
        self.time_outs: int = 2

        self.on_field: Set[int] = set([])
        self.on_bench: Set[int] = set([])
        self.unavailable: Set[int] = set(
            []
        )

        self.substitution_history: List[Tuple[int, int]] = (
            []
        )

        for player in players:
            self.players_statistics[player.dorsal] = PlayerStatistics()
            self.data[player.dorsal] = player

    def reset(self):
        self.statistics = TeamStatistics(self.name)
        for player_dorsal in self.data.keys():
            self.players_statistics[player_dorsal] = PlayerStatistics()

    def to_json(self) -> dict:
        return {
            "statistics": self.statistics.__dict__,
            "on_field": list(self.on_field),
            "on_bench": list(self.on_bench),
            "substitution_history": self.substitution_history,
            "players_statistics": {
                k: v.__dict__ for k, v in self.players_statistics.items()
            },
        }

    def get_player_role(self, player_dorsal: int) -> str:
        player: PlayerData = self.data.get(player_dorsal)
        if player:
            return player.position
        else:
            raise Exception(
                f"No se encontró al jugador con dorsal {player_dorsal} en el equipo {self.name}"
            )

    def get_player(self, player_dorsal: int) -> PlayerData:
        player = self.data.get(player_dorsal)
        if player:
            return player
        else:
            raise Exception(
                f"No se encontró al jugador con dorsal {player_dorsal} en el equipo {self.name}"
            )
