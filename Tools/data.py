from typing import Dict, List, Set, Tuple

from .line_up import LineUp
from .player_data import PlayerData


class PlayerStatistics:
    """
    Estadísticas para un jugador individual de voleibol.
    """

    def __init__(self):
        self.points: int = 0  # Puntos anotados
        self.attacks: int = 0  # Ataques realizados
        self.errors: int = 0  # Errores cometidos
        self.blocks: int = 0  # Bloqueos exitosos
        self.aces: int = 0  # Servicios directos (aces)
        self.digs: int = 0  # Defensas exitosas (digs)
        self.receives: int = 0  # Recepciones exitosas
        self.serves: int = 0  # Servicios realizados
        self.sets: int = 0  # Sets efectivos

        # Estadísticas totales
        self.total_attacks: int = 0  # Ataques totales
        self.total_blocks: int = 0  # Bloqueos totales
        self.total_aces: int = 0  # Aces totales
        self.total_digs: int = 0
        self.total_receives: int = 0
        self.total_serves: int = 0
        self.total_sets: int = 0
        self.total_points: int = 0


class TeamStatistics:
    """
    Estadísticas de equipo para un partido de voleibol.
    """

    def __init__(self, team_name: str):
        self.team_name: str = team_name

        self.points: int = 0  # Puntos totales anotados por el equipo
        self.aces: int = 0  # Aces totales del equipo
        self.errors: int = 0  # Errores totales del equipo
        self.blocks: int = 0  # Bloqueos totales del equipo
        self.digs: int = 0  # Digs totales del equipo
        self.attacks: int = 0  # Ataques totales del equipo
        self.substitutions: int = 0  # Número de sustituciones realizadas
        self.serves: int = 0  # Servicios totales del equipo
        self.sets_won: int = 0  # Sets ganados por el equipo
        self.sets_lost: int = 0  # Sets perdidos por el equipo
        self.receives: int = 0  # Recepciones totales del equipo
        self.sets: int = 0  # Sets efectivos del equipo


class TeamData:
    """
    Representa los datos y el estado de un equipo de voleibol.
    """

    def __init__(self, name: str, players: List[PlayerData]) -> None:
        self.name = name
        self.line_up: None | LineUp = None
        self.data: Dict[int, PlayerData] = {}  # Mapea dorsal a datos del jugador
        self.statistics: TeamStatistics = TeamStatistics(name)
        self.players_statistics: Dict[int, PlayerStatistics] = {}
        self.time_outs: int = 2

        self.on_field: Set[int] = set([])  # Jugadores en cancha (dorsales)
        self.on_bench: Set[int] = set([])  # Jugadores en banca (dorsales)
        self.unavailable: Set[int] = set(
            []
        )  # Jugadores no disponibles (lesionados, etc.)

        self.substitution_history: List[Tuple[int, int]] = (
            []
        )  # Historial de sustituciones (dorsal_in, dorsal_out)

        for player in players:
            self.players_statistics[player.dorsal] = PlayerStatistics()
            self.data[player.dorsal] = player

    def reset(self):
        """
        Reinicia las estadísticas del equipo y de los jugadores.
        """
        self.statistics = TeamStatistics(self.name)
        for player_dorsal in self.data.keys():
            self.players_statistics[player_dorsal] = PlayerStatistics()

    def to_json(self) -> dict:
        """
        Convierte los datos del equipo a un diccionario JSON serializable.
        """
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
        """
        Obtiene el rol (posición) de un jugador basado en su dorsal.
        """
        player: PlayerData = self.data.get(player_dorsal)
        if player:
            return player.position
        else:
            raise Exception(
                f"No se encontró al jugador con dorsal {player_dorsal} en el equipo {self.name}"
            )

    def get_player(self, player_dorsal: int) -> PlayerData:
        """
        Obtiene los datos de un jugador basado en su dorsal.
        """
        player = self.data.get(player_dorsal)
        if player:
            return player
        else:
            raise Exception(
                f"No se encontró al jugador con dorsal {player_dorsal} en el equipo {self.name}"
            )
