from .player_data import PlayerData
from .line_up import LineUp
from typing import List, Dict, Set, Tuple


class StatisticsPlayer:
    """
    Estadísticas para un jugador individual de voleibol.
    """
    def __init__(self):
        self.points: int = 0            # Puntos anotados
        self.attacks: int = 0           # Ataques realizados
        self.kills: int = 0             # Ataques exitosos que resultan en punto
        self.errors: int = 0            # Errores cometidos
        self.blocks: int = 0            # Bloqueos exitosos
        self.aces: int = 0              # Servicios directos (aces)
        self.digs: int = 0              # Defensas exitosas (digs)
        self.receives: int = 0          # Recepciones exitosas
        self.serves: int = 0            # Servicios realizados
        self.assists: int = 0           # Asistencias (colocaciones exitosas)
        self.rotations: int = 0         # Rotaciones en las que participó
        self.minutes_played: int = 0    # Minutos jugados


class StatisticsTeam:
    """
    Estadísticas de equipo para un partido de voleibol.
    """
    def __init__(self, team_name: str):
        self.team_name: str = team_name
        self.points: int = 0            # Puntos totales anotados por el equipo
        self.aces: int = 0              # Aces totales del equipo
        self.errors: int = 0            # Errores totales del equipo
        self.blocks: int = 0            # Bloqueos totales del equipo
        self.digs: int = 0              # Digs totales del equipo
        self.assists: int = 0           # Asistencias totales del equipo
        self.attacks: int = 0           # Ataques totales del equipo
        self.kills: int = 0             # Kills totales del equipo
        self.rotations: int = 0         # Número de rotaciones realizadas
        self.substitutions: int = 0     # Número de sustituciones realizadas
        self.lineup: List[int] = []     # Lista de dorsales de los jugadores en la alineación


class TeamData:
    """
    Representa los datos y el estado de un equipo de voleibol.
    """
    def __init__(self, name: str, players: List[PlayerData]) -> None:
        self.name = name
        self.line_up: LineUp = None
        self.data: Dict[int, PlayerData] = {}  # Mapea dorsal a datos del jugador
        self.statistics: StatisticsTeam = StatisticsTeam(name)
        self.players_statistics: Dict[int, StatisticsPlayer] = {}

        self.on_field: Set[int] = set([])      # Jugadores en cancha (dorsales)
        self.on_bench: Set[int] = set([])      # Jugadores en banca (dorsales)
        self.unavailable: Set[int] = set([])   # Jugadores no disponibles (lesionados, etc.)

        self.substitution_history: List[Tuple[int, int]] = []  # Historial de sustituciones (dorsal_in, dorsal_out)

        for player in players:
            self.players_statistics[player.dorsal] = StatisticsPlayer()
            self.data[player.dorsal] = player

    def reset(self):
        """
        Reinicia las estadísticas del equipo y de los jugadores.
        """
        self.statistics = StatisticsTeam(self.name)
        for player_dorsal in self.data.keys():
            self.players_statistics[player_dorsal] = StatisticsPlayer()

    def to_json(self) -> dict:
        """
        Convierte los datos del equipo a un diccionario JSON serializable.
        """
        return {
            'statistics': self.statistics.__dict__,
            'on_field': list(self.on_field),
            'on_bench': list(self.on_bench),
            'substitution_history': self.substitution_history,
            'players_statistics': {k: v.__dict__ for k, v in self.players_statistics.items()},
        }

    def get_player_role(self, player_dorsal: int) -> str:
        """
        Obtiene el rol (posición) de un jugador basado en su dorsal.
        """
        player = self.data.get(player_dorsal)
        if player:
            return player.role
        else:
            raise Exception(f"No se encontró al jugador con dorsal {player_dorsal} en el equipo {self.name}")
