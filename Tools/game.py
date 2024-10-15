from typing import Tuple

from Tools.data import TeamData
from Tools.enum import T1, T2
from Tools.field import Field, GridField
from Tools.line_up import LineUp
from Tools.utils import coin_toss


class Game:
    """
    Controla el estado del juego, puntajes, rotaciones y reglas.
    """

    def __init__(self, t1: TeamData, t2: TeamData, cant_instances: int):
        self.last_team_touched: str | None = None
        self.last_player_touched: int | None = None
        self.instance = 0
        self.cant_instances: int = cant_instances
        self.field: Field = Field()
        self.t1: TeamData = t1
        self.t2: TeamData = t2
        self.t1_score = 0
        self.t2_score = 0
        self.t1_sets = 0
        self.t2_sets = 0
        self.current_set = 1
        self.max_sets = 5
        self.sets_to_win = 3
        self.points_to_win_set = 25
        self.serving_team = T2
        self.touches = {T1: 0, T2: 0}
        self.general_touches = 0
        self.ball_possession_team = self.serving_team
        self.rally_over = False
        self.has_ball_landed = False
        self.points_history = []

    def score_point(self, scorer_team: str):
        self.ball_possession_team = scorer_team
        if scorer_team == T1:
            if self.last_player_touched in self.t1.on_field:
                player_statics = self.t1.players_statistics[self.last_player_touched]
                player_statics.points += 1
                if self.general_touches <= 1:
                    player_statics.aces += 1
            self.t1_score += 1
            if self.t1_score == 25:
                team_statics = self.t1.statistics
                team_statics.sets += 1
            self.points_history.append(
                {"team": T1, "score": self.t1_score, "set": self.current_set}
            )
        else:
            if self.last_player_touched in self.t2.on_field:
                player_statics = self.t2.players_statistics[self.last_player_touched]
                player_statics.points += 1
                if self.general_touches <= 1:
                    player_statics.aces += 1
            self.t2_score += 1
            if self.t2_score == 25:
                team_statics = self.t2.statistics
                team_statics.sets += 1
            self.points_history.append(
                {"team": T2, "score": self.t2_score, "set": self.current_set}
            )

        # Cambiar servicio si el equipo anotó es diferente al que servía
        if self.serving_team != scorer_team:
            self.serving_team = scorer_team
            # Rotar jugadores del equipo que ganó el servicio
            if scorer_team == T1:
                self.field.rotate_players(scorer_team, self.t1.line_up, self.t2.line_up)
            else:
                self.field.rotate_players(scorer_team, self.t2.line_up, self.t1.line_up)

        # Reiniciar toques y estados
        self.touches[T1] = 0
        self.touches[T2] = 0
        self.general_touches = 0
        self.last_team_touched = None

        # Verificar si el set ha terminado
        if self.has_set_ended():
            self.end_set()
        else:
            # Reposicionar jugadores para el siguiente punto
            self.field.conf_line_ups(
                self.t1.line_up, self.t2.line_up, self.serving_team
            )

    def has_set_ended(self) -> bool:
        if (
                self.t1_score >= self.points_to_win_set
                or self.t2_score >= self.points_to_win_set
        ) and abs(self.t1_score - self.t2_score) >= 2:
            return True
        return False

    def end_set(self):
        # print(str(self.t1_score) + " **************** " + str(self.t2_score))
        if self.t1_score > self.t2_score:
            self.t1_sets += 1
        else:
            self.t2_sets += 1

        self.t1_score = 0
        self.t2_score = 0
        self.current_set += 1

        if self.t1_sets == self.sets_to_win or self.t2_sets == self.sets_to_win:
            self.end_match()
        else:
            self.field.reset()
            if self.current_set == 5:
                self.serving_team = T1 if coin_toss() else T2
            else:
                self.serving_team = T1 if self.current_set % 2 == 1 else T2

            self.field.conf_line_ups(
                self.t1.line_up,
                self.t2.line_up,
                "T2" if self.serving_team == T1 else "T1",
            )

    def end_match(self):
        if self.t1_sets > self.t2_sets:
            print("El equipo 1 ha ganado el partido")
        else:
            print("El equipo 2 ha ganado el partido")

    def reset(self):
        self.instance = 0
        self.field.reset()
        self.t1.reset()
        self.t2.reset()
        self.t1_score = 0
        self.t2_score = 0
        self.t1_sets = 0
        self.t2_sets = 0
        self.current_set = 1
        self.touches = {T1: 0, T2: 0}
        self.last_team_touched = None
        self.ball_possession_team = self.serving_team
        self.rally_over = False
        self.last_fault_team = None

    def conf_line_ups(self, line_up_h: LineUp, line_up_a: LineUp):
        self.t1.line_up = line_up_h
        self.t2.line_up = line_up_a
        self.field.conf_line_ups(line_up_h, line_up_a, self.serving_team)

        self.t1.on_field = set([p.player for p in line_up_h.line_up.values()])
        self.t2.on_field = set([p.player for p in line_up_a.line_up.values()])

        self.t1.on_bench = set(
            [p for p in self.t1.data.keys() if p not in self.t1.on_field]
        )
        self.t2.on_bench = set(
            [p for p in self.t2.data.keys() if p not in self.t2.on_field]
        )

        # Identificar al jugador que sirve inicialmente (posición 1)
        serving_grid = self.field.find_player_in_position(1, self.serving_team)
        if serving_grid:
            serving_grid.ball = True
        else:
            raise Exception("No se encontró el jugador que sirve")

    def is_start(self) -> bool:
        return self.instance == 0

    def is_finish(self) -> bool:
        return self.t1_sets == self.sets_to_win or self.t2_sets == self.sets_to_win

    def to_json(self):
        return {
            "t1": self.t1.to_json(),
            "t2": self.t2.to_json(),
        }

    def is_our_serve(self, team: str) -> bool:
        return self.serving_team == team

    def is_player_server(self, dorsal: int) -> bool:
        """
        Determines if the player with the given dorsal number is the server.

        Args:
            dorsal (int): The dorsal number of the player.

        Returns:
            bool: True if the player is the server, False otherwise.
        """
        grid = self.field.find_player(dorsal, self.serving_team)
        return grid.position == 1

    def is_ball_on_our_side(self, team: str) -> bool:
        """
        Determines if the ball is on our side of the field.

        Args:
            team (str): The team identifier ('T1' or 'T2').

        Returns:
            bool: True if the ball is on our side, False otherwise.
        """
        ball_grid = self.field.find_ball()
        if team == T1:
            return ball_grid.row < self.field.net_row
        else:
            return ball_grid.row > self.field.net_row

    def is_ball_coming_to_player(self, dorsal: int, team: str) -> bool:
        # Lógica simplificada para determinar si la pelota viene hacia el jugador
        player_grid = self.field.find_player(dorsal, team)
        ball_grid = self.field.find_ball()
        return (
                self.field.int_distance(
                    (player_grid.row, player_grid.col), (ball_grid.row, ball_grid.col)
                )
                <= 3
        )

    def is_opponent_attacking(self, team: str) -> bool:
        return self.last_team_touched != team

    def ball_in_our_court(self, team: str) -> bool:
        return self.ball_possession_team == team

    def revert_point(self, team: str):
        if team == T1:
            self.t1_score -= 1
        elif team == T2:
            self.t2_score -= 1
        else:
            raise Exception("Equipo inválido")

    def player_has_ball(self, dorsal: int, team: str) -> bool:
        grid = self.field.find_player(dorsal, team)
        return grid.ball

    def predict_ball_landing_position(self) -> Tuple[int, int]:
        # Lógica simplificada: devolver la posición actual de la pelota
        ball_grid = self.field.find_ball()
        return (ball_grid.row, ball_grid.col)

    def start_rally(self):
        # Inicializar variables necesarias al inicio de un rally
        self.touches = {T1: 0, T2: 0}
        self.last_team_touched = None
        # La posesión de la pelota comienza con el equipo que sirve
        self.ball_possession_team = self.serving_team
        self.rally_over = False

    def is_rally_over(self) -> bool:
        return self.rally_over

    def determine_point_winner(self) -> str:
        # Lógica para determinar el ganador del punto
        if self.last_fault_team:
            # El equipo contrario gana
            return T1 if self.last_fault_team == T2 else T2
        else:
            # El equipo que no cometió falta y tocó la pelota por última vez gana
            return (
                self.last_team_touched
                if self.last_team_touched
                else (T1 if self.serving_team == T2 else T2)
            )

    def get_team_score(self, team):
        return self.t1_score if team == T1 else self.t2_score

    # Method to return the player more close to the ball
    def get_closest_player_to_ball(self, team: str) -> int:
        ball_grid = self.field.find_ball()
        closest_player = None
        min_distance = float("inf")
        for player_id in self.t1.on_field if team == T1 else self.t2.on_field:
            player_grid = self.field.find_player(player_id, team)
            distance = self.field.int_distance(
                (player_grid.row, player_grid.col), (ball_grid.row, ball_grid.col)
            )
            if distance < min_distance:
                min_distance = distance
                closest_player = player_id
        return closest_player

    def move_ball(self, src: Tuple[int, int], dest: Tuple[int, int]) -> bool:
        return self.field.move_ball(src, dest)

    @staticmethod
    def get_opponent_team(team: str) -> str:
        return T1 if team == T2 else T2

    def role_position(
            self, role: str, team: str, destination: Tuple[int, int] = (0, 0)
    ) -> GridField:
        min_distance = float("inf")
        role_position = None
        counter = 0
        if role == "OH":
            for row in self.field.grid:
                for grid in row:
                    if grid.player != -1 and grid.team == team:
                        player_role = (
                            self.t1.get_player_role(grid.player)
                            if team == T1
                            else self.t2.get_player_role(grid.player)
                        )
                        if player_role == role:
                            counter += 1
                            distance = self.field.distance(
                                destination, (grid.row, grid.col)
                            )
                            if distance < min_distance:
                                min_distance = distance
                                role_position = grid
                            if counter == 2:
                                return role_position

        for row in self.field.grid:
            for grid in row:
                if grid.player != -1 and grid.team == team:
                    player_role = (
                        self.t1.get_player_role(grid.player)
                        if team == T1
                        else self.t2.get_player_role(grid.player)
                    )
                    if player_role == role:
                        return grid

    def closest_enemy_distance(self, src: Tuple[int, int], team: str) -> float:
        min_distance = float("inf")
        for row in self.field.grid:
            for grid in row:
                if grid.team != team:
                    distance = self.field.distance(src, (grid.row, grid.col))
                    if distance < min_distance:
                        min_distance = distance
        return min_distance

    def can_call_time_out(self, team: str) -> bool:
        return self.t1.time_outs > 0 if team == T1 else self.t2.time_outs > 0

    def register_time_out(self, team: str) -> None:
        if team == T1:
            self.t1.time_outs -= 1
        else:
            self.t2.time_outs -= 1

    def revert_timeout(self, team):
        if team == T1:
            self.t1.time_outs += 1
        else:
            self.t2.time_outs += 1

    def get_team_sets(self, team: str):
        return self.t1_sets if team == T1 else self.t1_sets
