from typing import Tuple, Optional
from .data import TeamData
from line_up import LineUp
from field import Field
from enum import HOME, AWAY


class Game:
    """
    Controla el estado del juego, puntajes, rotaciones y reglas.
    """
    def __init__(self, home: TeamData, away: TeamData, cant_instances: int):
        self.instance = 0
        self.cant_instances: int = cant_instances
        self.field: Field = Field()
        self.home: TeamData = home
        self.away: TeamData = away
        self.home_score = 0
        self.away_score = 0
        self.home_sets = 0
        self.away_sets = 0
        self.current_set = 1
        self.max_sets = 5
        self.points_to_win_set = 25
        self.serving_team = HOME
        self.touches = {HOME: 0, AWAY: 0}
        self.last_team_touched: Optional[str] = None
        self.ball_possession_team = self.serving_team
        self.rally_over = False
        self.last_fault_team: Optional[str] = None  # Equipo que cometió una falta

    def score_point(self, team: str):
        if team == HOME:
            self.home_score += 1
        elif team == AWAY:
            self.away_score += 1
        else:
            raise Exception("Equipo inválido")

        # Cambiar servicio si el equipo anotó es diferente al que servía
        if self.serving_team != team:
            self.serving_team = team
            # Rotar jugadores del equipo que ganó el servicio
            if team == HOME:
                self.field.rotate_players(team, self.home.line_up)
            else:
                self.field.rotate_players(team, self.away.line_up)

        # Reiniciar toques y estados
        self.touches[HOME] = 0
        self.touches[AWAY] = 0
        self.last_team_touched = None
        self.last_fault_team = None

        # Verificar si el set ha terminado
        if self.has_set_ended():
            self.end_set()
        else:
            # Reposicionar jugadores para el siguiente punto
            self.field.conf_line_ups(self.home.line_up, self.away.line_up)

    def has_set_ended(self) -> bool:
        if (self.home_score >= self.points_to_win_set or self.away_score >= self.points_to_win_set) and abs(
                self.home_score - self.away_score) >= 2:
            return True
        return False

    def end_set(self):
        if self.home_score > self.away_score:
            self.home_sets += 1
        else:
            self.away_sets += 1

        self.home_score = 0
        self.away_score = 0
        self.current_set += 1

        if self.home_sets > self.max_sets // 2 or self.away_sets > self.max_sets // 2:
            self.end_match()
        else:
            self.field.reset()
            self.serving_team = HOME if self.current_set % 2 == 1 else AWAY
            # Reiniciar posiciones de los jugadores
            self.home.line_up.reset_positions()
            self.away.line_up.reset_positions()
            self.field.conf_line_ups(self.home.line_up, self.away.line_up)

    def end_match(self):
        if self.home_sets > self.away_sets:
            print("El equipo de casa ha ganado el partido")
        else:
            print("El equipo visitante ha ganado el partido")

    def reset(self):
        self.instance = 0
        self.field.reset()
        self.home.reset()
        self.away.reset()
        self.home_score = 0
        self.away_score = 0
        self.home_sets = 0
        self.away_sets = 0
        self.current_set = 1
        self.touches = {HOME: 0, AWAY: 0}
        self.last_team_touched = None
        self.ball_possession_team = self.serving_team
        self.rally_over = False
        self.last_fault_team = None

    def conf_line_ups(self, line_up_h: LineUp, line_up_a: LineUp):
        self.home.line_up = line_up_h
        self.away.line_up = line_up_a
        self.field.conf_line_ups(line_up_h, line_up_a)

        self.home.on_field = set(
            [p.player for p in line_up_h.line_up.values()])
        self.away.on_field = set(
            [p.player for p in line_up_a.line_up.values()])

        self.home.on_bench = set([
            p for p in self.home.data.keys() if p not in self.home.on_field])
        self.away.on_bench = set([
            p for p in self.away.data.keys() if p not in self.away.on_field])

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
        return self.instance >= self.cant_instances + 1 or self.home_sets > self.max_sets // 2 or self.away_sets > self.max_sets // 2

    def to_json(self):
        return {
            'home': self.home.to_json(),
            'away': self.away.to_json(),
        }

    # Métodos para verificar estado del juego
    def is_our_serve(self, team: str) -> bool:
        return self.serving_team == team

    def is_player_server(self, dorsal: int) -> bool:
        # El jugador en posición 1 es el servidor
        grid = self.field.find_player(dorsal, self.serving_team)
        return grid.position == 1

    def is_ball_on_our_side(self, team: str) -> bool:
        ball_grid = self.field.find_ball()
        if team == HOME:
            return ball_grid.row >= self.field.net_row
        else:
            return ball_grid.row < self.field.net_row

    def is_ball_coming_to_player(self, dorsal: int, team: str) -> bool:
        # Lógica simplificada para determinar si la pelota viene hacia el jugador
        player_grid = self.field.find_player(dorsal, team)
        ball_grid = self.field.find_ball()
        return self.field.int_distance((player_grid.row, player_grid.col), (ball_grid.row, ball_grid.col)) <= 1

    def is_opponent_attacking(self) -> bool:
        # Lógica simplificada para determinar si el oponente está atacando
        return self.last_team_touched != self.serving_team

    def ball_in_opponent_court(self) -> bool:
        ball_grid = self.field.find_ball()
        return (ball_grid.row < self.field.net_row and self.serving_team == HOME) or (
                ball_grid.row >= self.field.net_row and self.serving_team == AWAY)

    def ball_in_our_court(self) -> bool:
        return not self.ball_in_opponent_court()

    def revert_point(self, team: str):
        if team == HOME:
            self.home_score -= 1
        elif team == AWAY:
            self.away_score -= 1
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
        self.touches = {HOME: 0, AWAY: 0}
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
        self.touches[HOME] = 0
        self.touches[AWAY] = 0
        # Cambiar posesión de la pelota
        self.ball_possession_team = HOME if self.ball_possession_team == AWAY else AWAY

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
            return HOME if self.last_fault_team == AWAY else AWAY
        else:
            # El equipo que no cometió falta y tocó la pelota por última vez gana
            return self.last_team_touched if self.last_team_touched else (HOME if self.serving_team == AWAY else AWAY)