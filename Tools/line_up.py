from abc import ABC
from typing import Dict, Optional

from Tools.enum import PlayerRole, dict_t1, dict_t2
from Tools.player_data import PlayerData


class LineUpGrid:
    def __init__(
            self, row: int, col: int, position_number: int, player_role: str
    ) -> None:
        self.row: int = row
        self.col: int = col
        self.player: Optional[int] = (
            None
        )
        self.position_number: int = position_number
        self.conf: str = "NORMAL"
        self.player_role: str = player_role

    def conf_player(self, player: PlayerData):
        in_role = (
                player.position == self.player_role or self.player_role in player.roles
        )
        self._set_statistics(player, in_role)
        self.player = player.dorsal

    def set_statistics(self, player_data: PlayerData) -> None:
        in_role = (
                player_data.position == self.player_role
                or self.player_role in player_data.roles
        )
        self._set_statistics(player_data, in_role)

    def _set_statistics(self, player_data: PlayerData, in_role: bool) -> None:
        if not in_role:
            player_data.p_attack = max(0, player_data.p_attack - 5)
            player_data.p_block = max(0, player_data.p_block - 5)
            player_data.p_serve = max(0, player_data.p_serve - 5)
            player_data.p_receive = max(0, player_data.p_receive - 5)
            player_data.p_set = max(0, player_data.p_set - 5)
            player_data.p_dig = max(0, player_data.p_dig - 5)
            player_data.overall = player_data.calculate_overall()


class LineUp(ABC):
    def __init__(self) -> None:
        self.line_up: Dict[int, LineUpGrid] = {}

    def conf_players(self, players: Dict[int, PlayerData]) -> None:
        for position_number, player in players.items():
            if position_number in self.line_up:
                self.line_up[position_number].conf_player(player)
            else:
                raise ValueError(
                    f"Número de posición {position_number} no está en la alineación."
                )

    def get_player_position(self, player_dorsal: int) -> Optional[LineUpGrid]:
        for grid in self.line_up.values():
            if grid.player == player_dorsal:
                return grid
        return None

    def get_player_role(self, player_dorsal: int) -> Optional[str]:
        line_up_position = self.get_player_position(player_dorsal)
        return line_up_position.player_role if line_up_position else None

    def rotate(self, team: str):
        position_numbers = [1, 2, 3, 4, 5, 6]
        rotated_positions = position_numbers[-1:] + position_numbers[:-1]
        temp_line_up = {}
        for old_pos_num, new_pos_num in zip(position_numbers, rotated_positions):
            for grid in self.line_up.values():
                if grid.position_number == old_pos_num:
                    grid.position_number = new_pos_num
                    if team == "T1":
                        grid.row, grid.col = dict_t1[new_pos_num]
                    elif team == "T2":
                        grid.row, grid.col = dict_t2[new_pos_num]
                    else:
                        raise ValueError(f"Unknown team: {team}")
                    temp_line_up[new_pos_num] = grid
                    break
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

    def substitute_player(self, player_out: int, player_in: int) -> None:
        for grid in self.line_up.values():
            if grid.player == player_out:
                grid.player = player_in
                return
        raise ValueError(f"No se encontró al jugador {player_out} en la alineación.")


class StandardVolleyballLineUp(LineUp):
    def __init__(self, team_side: str) -> None:
        super().__init__()
        self.court_length = 18
        self.line_up = self._create_positions(team_side)

    def _create_positions(self, team_side: str) -> Dict[int, LineUpGrid]:
        positions = {
            3: LineUpGrid(dict_t1[3][0], dict_t1[3][1], 3, PlayerRole.MIDDLE_BLOCKER),  # Posición 1
            5: LineUpGrid(dict_t1[5][0], dict_t1[5][1], 5, PlayerRole.OUTSIDE_HITTER),  # Posición 2
            6: LineUpGrid(dict_t1[6][0], dict_t1[6][1], 6, PlayerRole.LIBERO),  # Posición 3
            1: LineUpGrid(dict_t1[1][0], dict_t1[1][1], 1, PlayerRole.SETTER),  # Posición 4
            2: LineUpGrid(dict_t1[2][0], dict_t1[2][1], 2, PlayerRole.OUTSIDE_HITTER),  # Posición 5
            4: LineUpGrid(dict_t1[4][0], dict_t1[4][1], 4, PlayerRole.OPPOSITE_HITTER),  # Posición 6
        }

        if team_side == "T2":
            for grid in positions.values():
                match grid.position_number:
                    case 1:
                        grid.row, grid.col = dict_t2[1]
                    case 2:
                        grid.row, grid.col = dict_t2[2]
                    case 3:
                        grid.row, grid.col = dict_t2[3]
                    case 4:
                        grid.row, grid.col = dict_t2[4]
                    case 5:
                        grid.row, grid.col = dict_t2[5]
                    case 6:
                        grid.row, grid.col = dict_t2[6]

        return positions
