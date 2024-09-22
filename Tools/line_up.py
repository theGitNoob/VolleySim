from abc import ABC
from typing import Dict

from .player_data import PlayerData

# Estrategias
OFFENSIVE = 'OFFENSIVE'
DEFENSIVE = 'DEFENSIVE'
NORMAL = 'NORMAL'

# Roles de jugador en voleibol
SETTER = 'SETTER'  # Colocador
MIDDLE_BLOCKER = 'MIDDLE_BLOCKER'  # Central
OUTSIDE_HITTER = 'OUTSIDE_HITTER'  # Punta o Atacante Exterior
OPPOSITE_HITTER = 'OPPOSITE_HITTER'  # Opuesto
LIBERO = 'LIBERO'  # Líbero


class LineUpGrid:
    def __init__(self, row: int, col: int, position_number: int, player_role: str) -> None:
        self.row: int = row  # Posición en la cancha (fila)
        self.col: int = col  # Posición en la cancha (columna)
        self.player: int = -1  # Número de camiseta del jugador
        self.position_number: int = position_number  # Posición de rotación (1-6)
        self.conf: str = NORMAL  # Estrategia actual
        self.player_role: str = player_role  # Rol del jugador

    def conf_player(self, player: PlayerData):
        self._set_statistics(player, player.preferred_role == self.player_role)
        self.player: int = player.number  # Asignar número de jugador

    def set_statistics(self, player_data: PlayerData) -> None:
        self._set_statistics(
            player_data, player_data.preferred_role == self.player_role)

    def _set_statistics(self, player_data: PlayerData, in_role: bool) -> None:
        if not in_role:
            # Penalizar estadísticas si el jugador no está en su rol preferido
            player_data.spike -= 5
            player_data.block -= 5
            player_data.serve -= 5
            player_data.receive -= 5
            player_data.set -= 5
            player_data.dig -= 5
            player_data.overall -= 5


class LineUp(ABC):
    def __init__(self) -> None:
        self.line_up: Dict[int, LineUpGrid] = {}  # Diccionario de posiciones (1-6)

    def conf_players(self, players: Dict[int, PlayerData]) -> None:
        for position_number, player in players.items():
            self.line_up[position_number].conf_player(player)

    def get_player_position(self, player_number: int) -> LineUpGrid | None:
        for grid in self.line_up.values():
            if grid.player == player_number:
                return grid
        return None

    def get_player_role(self, player_number: int) -> str:
        line_up_position = self.get_player_position(player_number)
        return line_up_position.player_role if line_up_position else None

    def rotate(self):
        # Rotar posiciones en sentido de las agujas del reloj
        position_numbers = [1, 6, 5, 4, 3, 2]
        rotated_positions = position_numbers[-1:] + position_numbers[:-1]
        temp_line_up = {}
        for old_pos_num, new_pos_num in zip(position_numbers, rotated_positions):
            temp_line_up[new_pos_num] = self.line_up[old_pos_num]
            temp_line_up[new_pos_num].position_number = new_pos_num
        self.line_up = temp_line_up


class StandardVolleyballLineUp(LineUp):
    def __init__(self) -> None:
        super().__init__()
        # Definir las posiciones iniciales en la cancha
        self.line_up = {
            1: LineUpGrid(16, 4, 1, OPPOSITE_HITTER),  # Posición 1 (Zaguero Derecho)
            2: LineUpGrid(12, 6, 2, OUTSIDE_HITTER),  # Posición 2 (Delantero Derecho)
            3: LineUpGrid(12, 4, 3, MIDDLE_BLOCKER),  # Posición 3 (Delantero Central)
            4: LineUpGrid(12, 2, 4, OUTSIDE_HITTER),  # Posición 4 (Delantero Izquierdo)
            5: LineUpGrid(16, 2, 5, LIBERO),  # Posición 5 (Zaguero Izquierdo)
            6: LineUpGrid(16, 6, 6, SETTER),  # Posición 6 (Zaguero Central)
        }


# Ejemplo de uso
# Asumiendo que la clase PlayerData tiene los atributos necesarios
# Crear instancias de PlayerData para cada jugador
player1 = PlayerData(number=1, preferred_role=OPPOSITE_HITTER, spike=80, block=70, serve=75, receive=65, set=60, dig=70,
                     overall=75)
player2 = PlayerData(number=2, preferred_role=OUTSIDE_HITTER, spike=85, block=65, serve=70, receive=75, set=65, dig=80,
                     overall=78)
player3 = PlayerData(number=3, preferred_role=MIDDLE_BLOCKER, spike=80, block=85, serve=65, receive=60, set=55, dig=65,
                     overall=77)
player4 = PlayerData(number=4, preferred_role=OUTSIDE_HITTER, spike=83, block=68, serve=72, receive=78, set=67, dig=82,
                     overall=79)
player5 = PlayerData(number=5, preferred_role=LIBERO, spike=50, block=50, serve=60, receive=90, set=70, dig=90,
                     overall=80)
player6 = PlayerData(number=6, preferred_role=SETTER, spike=70, block=65, serve=75, receive=70, set=85, dig=75,
                     overall=78)

# Crear la alineación y configurar los jugadores
lineup = StandardVolleyballLineUp()
players = {
    1: player1,
    2: player2,
    3: player3,
    4: player4,
    5: player5,
    6: player6
}
lineup.conf_players(players)

# Rotar las posiciones
lineup.rotate()

# Obtener la posición y rol de un jugador
player_number = 1
grid = lineup.get_player_position(player_number)
print(f"El jugador {player_number} está en la posición {grid.position_number} como {grid.player_role}")
