import math
from typing import List, Optional, Tuple

from Tools.enum import T1, T2
from Tools.line_up import LineUp


class GridField:
    """
    Representa una celda en el campo de voleibol.
    """

    def __init__(
        self,
        row: int,
        col: int,
        player: int = -1,
        ball: bool = False,
        team: str = "",
        is_net: bool = False,
        position: int = 0,
    ) -> None:
        self.row: int = row
        self.col: int = col
        self.ball: bool = ball
        self.player: int = player
        self.team: str = team
        self.is_net: bool = is_net
        self.position: int = position  # Posición de rotación (1-6)

    def is_empty(self) -> bool:
        return self.player == -1

    def is_contiguous(self, g: "GridField"):
        return (abs(self.row - g.row) == 1 and abs(self.col - g.col) == 1) or (
            abs(self.row - g.row) + abs(self.col - g.col) == 1
        )

    def str_code(self) -> str:
        if self.player == -1:
            return "    "
        return f'{self.player:02}{self.team[0]}{"B" if self.ball else " "}'

    def __str__(self) -> str:
        if self.is_net:
            return "||"  # Representa la red
        elif self.ball:
            return "🏐"  # Representa la pelota de voleibol
        elif self.player != -1:
            color = "\033[34m" if self.team == T1 else "\033[31m"
            return f"{color}{self.player:02}\033[0m"
        else:
            return "XX"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GridField):
            return False
        return self.row == other.row and self.col == other.col


class Field:
    """
    Gestiona el campo de juego y las operaciones relacionadas.
    """

    def __init__(self, rows: int = 19, columns: int = 9):
        self.rows = rows
        self.columns = columns
        self.grid: List[List[GridField]] = [
            [GridField(r, c) for c in range(columns)] for r in range(rows)
        ]
        self.net_row = 9  # Fila de la red
        for c in range(columns):
            self.grid[self.net_row][c].is_net = True

    def reset(self):
        self.grid = [
            [GridField(r, c) for c in range(self.columns)] for r in range(self.rows)
        ]
        for c in range(self.columns):
            self.grid[self.net_row][c].is_net = True

    def conf_line_ups(
            self, line_up_h: LineUp, line_up_a: LineUp, server_team: str | None = None
    ):
        for grid in self.grid:
            for g in grid:
                if g.row < 9:
                    g.team = "T1"
                elif g.row > 9:
                    g.team = "T2"
                g.player = -1
                g.position = 0
                g.ball = False

        # Configurar alineaciones para el equipo de casa
        for pos_number, grid_info in line_up_h.line_up.items():
            if pos_number == 1 and server_team == T1:
                self.grid[grid_info.row][grid_info.col].ball = True
            r, c, player_id = grid_info.row, grid_info.col, grid_info.player
            self.grid[r][c].player = player_id
            self.grid[r][c].team = T1
            self.grid[r][c].position = pos_number  # Posición de rotación

        # Configurar alineaciones para el equipo visitante
        for pos_number, grid_info in line_up_a.line_up.items():
            if pos_number == 1 and server_team == T2:
                self.grid[grid_info.row][grid_info.col].ball = True
            r, c, player_id = grid_info.row, grid_info.col, grid_info.player
            self.grid[r][c].player = player_id
            self.grid[r][c].team = T2
            self.grid[r][c].position = pos_number  # Posición de rotación

    def find_player_in_position(
        self, position_number: int, team: str
    ) -> Optional[GridField]:
        """
        Encuentra al jugador en una posición de rotación específica para un equipo.
        """
        for row in self.grid:
            for grid in row:
                if grid.team == team and grid.position == position_number:
                    return grid
        return None

    def move_ball(self, src: Tuple[int, int], dest: Tuple[int, int]) -> bool:
        x_src, y_src = src
        x_dest, y_dest = dest

        if not self.grid[x_src][y_src].ball:
            raise Exception("La pelota no está en la posición de origen")

        # Mover la pelota
        self.grid[x_src][y_src].ball = False
        self.grid[x_dest][y_dest].ball = True

        # Detectar si la pelota cruzó la red
        ball_crossed_net = (x_src < self.net_row <= x_dest) or (
                x_src > self.net_row >= x_dest
        )

        if ball_crossed_net:
            return True
        else:
            return False

    def rotate_players(self, team: str, line_up_to_rotate: LineUp, line_up: LineUp):
        # Rotar las posiciones en el line-up
        line_up_to_rotate.rotate(team)

        # Limpiar las posiciones actuales en el campo
        for row in self.grid:
            for grid in row:
                if grid.team == team:
                    grid.player = -1
                    grid.team = ""
                    grid.position = 0

        # Reubicar los jugadores en el campo según el line-up rotado
        for pos_number, grid_info in line_up_to_rotate.line_up.items():
            if pos_number == 1:
                self.grid[grid_info.row][grid_info.col].ball = True
            r, c, player_id = grid_info.row, grid_info.col, grid_info.player
            self.grid[r][c].player = player_id
            self.grid[r][c].team = team
            self.grid[r][c].position = pos_number

    def move_player(self, src: Tuple[int, int], dest: Tuple[int, int]):
        x_src, y_src = src
        x_dest, y_dest = dest
        player_field = self.grid[x_src][y_src]

        if player_field.player == -1:
            raise Exception("El jugador no está en la posición de origen")

        # Mover jugador si la posición de destino está vacía
        if self.grid[x_dest][y_dest].player != -1:
            return
            # raise Exception("La posición de destino ya está ocupada")

        # Actualizar posiciones
        self.grid[x_dest][y_dest].player = player_field.player
        self.grid[x_dest][y_dest].team = player_field.team
        self.grid[x_dest][y_dest].position = player_field.position

        self.grid[x_src][y_src].player = -1
        self.grid[x_src][y_src].team = ""
        self.grid[x_src][y_src].position = 0

    def is_valid_grid(self, grid: Tuple[int, int]) -> bool:
        x, y = grid
        return 0 <= x < self.rows and 0 <= y < self.columns

    @staticmethod
    def distance(src: Tuple[int, int], dest: Tuple[int, int]) -> float:
        xs, ys = src
        xd, yd = dest
        return math.sqrt((xs - xd) ** 2 + (ys - yd) ** 2)

    @staticmethod
    def int_distance(src: Tuple[int, int], dest: Tuple[int, int]) -> int:
        xs, ys = src
        xd, yd = dest
        return max(abs(xs - xd), abs(ys - yd))

    def find_player(self, dorsal: int, team: str) -> GridField:
        for row in self.grid:
            for grid in row:
                if grid.player == dorsal and grid.team == team:
                    return grid
        raise Exception(
            f"No se encontró al jugador con el dorsal {dorsal} del equipo {team} en el campo"
        )

    def find_ball(self) -> GridField:
        for row in self.grid:
            for grid in row:
                if grid.ball:
                    return grid
        raise Exception("La pelota no está en el campo")

    def neighbor_grids(self, src: GridField, max_distance: float) -> List[GridField]:
        x, y = (src.row, src.col)
        grids: List[GridField] = []
        for row in self.grid:
            for grid in row:
                distance = self.distance((x, y), (grid.row, grid.col))
                if distance <= max_distance:
                    grids.append(grid)
        return grids

    def __str__(self) -> str:
        field_str = ""
        for r in range(self.rows):
            for c in range(self.columns):
                grid = self.grid[r][c]
                field_str += str(grid) + " "
            field_str += "\n"
        return field_str

    def str_code(self) -> str:
        field_str = ""
        for r in range(self.rows):
            for c in range(self.columns):
                field_str += self.grid[r][c].str_code() + " "
            field_str += "\n"
        return field_str
