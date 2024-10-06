from abc import ABC
from typing import Dict, Optional

from Tools.enum import PlayerRole
from Tools.player_data import PlayerData

# Estrategias
OFFENSIVE = "OFFENSIVE"
DEFENSIVE = "DEFENSIVE"
NORMAL = "NORMAL"


class LineUpGrid:
    def __init__(self, row: int, col: int, position_number: int, player_role: str) -> None:
        self.row: int = row  # Posición en la cancha (fila)
        self.col: int = col  # Posición en la cancha (columna)
        self.player: Optional[int] = None  # Dorsal del jugador (None si no hay jugador asignado)
        self.position_number: int = position_number  # Posición de rotación (1-6)
        self.conf: str = NORMAL  # Estrategia actual
        self.player_role: str = player_role  # Rol del jugador

    def conf_player(self, player: PlayerData):
        in_role = player.position == self.player_role or self.player_role in player.roles
        self._set_statistics(player, in_role)
        self.player = player.dorsal  # Asignar dorsal del jugador

    def set_statistics(self, player_data: PlayerData) -> None:
        in_role = player_data.position == self.player_role or self.player_role in player_data.roles
        self._set_statistics(player_data, in_role)

    def _set_statistics(self, player_data: PlayerData, in_role: bool) -> None:
        if not in_role:
            # Penalizar estadísticas si el jugador no está en su rol preferido
            player_data.p_attack = max(0, player_data.p_attack - 5)
            player_data.p_block = max(0, player_data.p_block - 5)
            player_data.p_serve = max(0, player_data.p_serve - 5)
            player_data.p_receive = max(0, player_data.p_receive - 5)
            player_data.p_set = max(0, player_data.p_set - 5)
            player_data.p_dig = max(0, player_data.p_dig - 5)
            player_data.overall = player_data.calculate_overall()


class LineUp(ABC):
    def __init__(self) -> None:
        self.line_up: Dict[int, LineUpGrid] = {}  # Diccionario de posiciones (1-6)

    def conf_players(self, players: Dict[int, PlayerData]) -> None:
        for position_number, player in players.items():
            if position_number in self.line_up:
                self.line_up[position_number].conf_player(player)
            else:
                raise ValueError(f"Número de posición {position_number} no está en la alineación.")

    def get_player_position(self, player_dorsal: int) -> Optional[LineUpGrid]:
        for grid in self.line_up.values():
            if grid.player == player_dorsal:
                return grid
        return None

    def get_player_role(self, player_dorsal: int) -> Optional[str]:
        line_up_position = self.get_player_position(player_dorsal)
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

    def reset_positions(self, team_side: str) -> None:
        return

    def add_player(self, player: PlayerData, role: str) -> None:
        for grid in self.line_up.values():
            if grid.player is None and grid.player_role.value == role:
                grid.conf_player(player)
                return
        raise ValueError(f"No hay posición disponible para el rol {role}.")

    def select_next_player(self) -> int:
        for grid in self.line_up.values():
            if grid.player is not None:
                return grid.player
        raise ValueError("No hay jugadores en la alineación.")


class StandardVolleyballLineUp(LineUp):
    def __init__(self, team_side: str) -> None:
        super().__init__()
        self.court_length = 18
        self.line_up = self._create_positions(team_side)

    def _create_positions(self, team_side: str) -> Dict[int, LineUpGrid]:
        # Posiciones base (Equipo 1)
        positions = {
            1: LineUpGrid(8, 4, 3, PlayerRole.MIDDLE_BLOCKER),  # Posición 1
            2: LineUpGrid(1, 7, 2, PlayerRole.OUTSIDE_HITTER),  # Posición 2
            3: LineUpGrid(4, 4, 6, PlayerRole.LIBERO),  # Posición 3
            4: LineUpGrid(1, 1, 1, PlayerRole.SETTER),  # Posición 4
            5: LineUpGrid(7, 1, 5, PlayerRole.OUTSIDE_HITTER),  # Posición 5
            6: LineUpGrid(7, 7, 4, PlayerRole.OPPOSITE_HITTER),  # Posición 6
        }

        if team_side == "T2":
            # Reflejar las posiciones en el eje vertical
            for grid in positions.values():
                grid.row = self.court_length - grid.row
        return positions
