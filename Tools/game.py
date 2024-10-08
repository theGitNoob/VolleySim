import time
from typing import Optional, Tuple

from Tools.data import TeamData
from Tools.enum import T1, T2
from Tools.field import Field
from Tools.line_up import LineUp
from Tools.utils import coin_toss


class Game:
    """
    Controla el estado del juego, puntajes, rotaciones y reglas.
    """

    def __init__(self, t1: TeamData, t2: TeamData, cant_instances: int):
        self.last_team_touched = None
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
        self.serving_team = T1
        self.touches = {T1: 0, T2: 0}
        self.last_team_touched: str | None
        self.ball_possession_team = self.serving_team
        self.rally_over = False
        self.last_fault_team: Optional[str] = None  # Equipo que cometió una falta

    def score_point(self, team: str):
        if team == T1:
            self.t1_score += 1
        else:
            self.t2_score += 1

        # Cambiar servicio si el equipo anotó es diferente al que servía
        if self.serving_team != team:
            self.serving_team = team
            # Rotar jugadores del equipo que ganó el servicio
            if team == T1:
                self.field.rotate_players(team, self.t1.line_up, self.t2.line_up)
            else:
                self.field.rotate_players(team, self.t2.line_up, self.t1.line_up)

        # Reiniciar toques y estados
        self.touches[T1] = 0
        self.touches[T2] = 0
        self.last_team_touched = None
        # TODO: Check if var has sense
        self.last_fault_team = None

        # Verificar si el set ha terminado
        if self.has_set_ended():
            self.end_set()
        else:
            # Reposicionar jugadores para el siguiente punto
            self.field.conf_line_ups(self.t1.line_up, self.t2.line_up)

    def has_set_ended(self) -> bool:
        if (
            self.t1_score >= self.points_to_win_set
            or self.t2_score >= self.points_to_win_set
        ) and abs(self.t1_score - self.t2_score) >= 2:
            return True
        return False

    def end_set(self):
        print(str(self.t1_score) + " **************** " + str(self.t2_score))
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
            print(self.field)
            time.sleep(20)
            self.field.reset()
            if self.current_set == 5:
                self.serving_team = T1 if coin_toss() else T2
            else:
                self.serving_team = T1 if self.current_set % 2 == 1 else T2
            # Reiniciar posiciones de los jugadores
            self.t1.line_up.reset_positions("T1")
            self.t2.line_up.reset_positions(self.t2.name)
            # TODO hacer un global_serving_team para hacer el cambio de servicio despues de cada set
            self.field.conf_line_ups(
                self.t1.line_up,
                self.t2.line_up,
                "T2" if self.serving_team == T1 else "T1",
            )
            print("Nuevo campo")
            print(self.field)

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
        self.field.conf_line_ups(line_up_h, line_up_a)

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

    def is_middle(self) -> bool:
        return self.instance == self.cant_instances // 2 + 1

    def is_finish(self) -> bool:
        return (
            self.instance >= self.cant_instances + 1
            or self.t1_sets > self.max_sets // 2
            or self.t2_sets > self.max_sets // 2
        )

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
            return ball_grid.row >= self.field.net_row
        else:
            return ball_grid.row < self.field.net_row

    def is_ball_coming_to_player(self, dorsal: int, team: str) -> bool:
        # Lógica simplificada para determinar si la pelota viene hacia el jugador
        player_grid = self.field.find_player(dorsal, team)
        ball_grid = self.field.find_ball()
        return (
            self.field.int_distance(
                (player_grid.row, player_grid.col), (ball_grid.row, ball_grid.col)
            )
            <= 1
        )

    def is_opponent_attacking(self) -> bool:
        # Lógica simplificada para determinar si el oponente está atacando
        return self.last_team_touched != self.serving_team

    def ball_in_opponent_court(self) -> bool:
        ball_grid = self.field.find_ball()
        return (ball_grid.row < self.field.net_row and self.serving_team == T1) or (
            ball_grid.row >= self.field.net_row and self.serving_team == T2
        )

    def ball_in_our_court(self) -> bool:
        return not self.ball_in_opponent_court()

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
        self.last_fault_team = None

    def is_rally_over(self) -> bool:
        return self.rally_over

    def handle_end_of_rally(self):
        winning_team = self.determine_point_winner()
        self.score_point(winning_team)

    def register_touch(self, team: str):
        self.touches[team] += 1
        self.last_team_touched = team

        if self.touches[team] > 3:
            # Excedió los 3 toques
            self.register_fault(team)

    def register_fault(self, team: str):
        self.last_fault_team = team
        self.rally_over = True

    def ball_crossed_net(self):
        # Reiniciar toques al cruzar la red
        self.touches[T1] = 0
        self.touches[T2] = 0
        # Cambiar posesión de la pelota
        self.ball_possession_team = T1 if self.ball_possession_team == T2 else T2

    def ball_landed(self, team: str):
        # La pelota cayó al suelo
        self.register_fault(team)

    def player_contact_ball(self, player_id: int, team: str):
        # Llamar cuando un jugador toca la pelota
        self.register_touch(team)

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

    def move_ball(self, src: Tuple[int, int], dest: Tuple[int, int]) -> str:
        return self.field.move_ball(src, dest)
