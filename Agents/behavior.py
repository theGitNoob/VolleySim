# behavior.py

import random
from typing import Tuple

from Tools.enum import T1
from Tools.game import Game
from Tools.line_up import LineUp

from .actions import (Action, Attack, Block, Dig, Move, Nothing, Receive,
                      Serve, Set)


class Behavior:
    def __init__(self, importance: float = 1.0) -> None:
        self.importance = importance

    def eval(self, action: Action, game: Game) -> float:
        pass

    def change_importance(self, importance: float) -> None:
        self.importance = importance


class RandomBehavior(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        return random.random() * self.importance


class ReturnToPositionBehavior(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        team = game.t1 if action.team == T1 else game.t2
        line_up_position = team.line_up.get_player_position(action.player)
        line_up_position = (line_up_position.row, line_up_position.col)

        if isinstance(action, Move):
            source = action.src
            destination = action.dest
            # Si el jugador se mueve más cerca de su posición asignada
            if game.field.distance(destination, line_up_position) < game.field.distance(
                source, line_up_position
            ):
                return self.importance
            else:
                return 0.0
        else:
            return 0.0


class DefensiveBehavior(Behavior):
    def eval(self, action: Action, game: Game, line_up: LineUp) -> float:
        team = game.t1 if action.team == T1 else game.t2
        current_position = line_up.get_player_position(action.player)

        value = 0.0

        # Determinar si el jugador está en posición delantera o trasera
        is_front_row = self.is_front_row(current_position, action.team, game)

        if game.ball_in_opponent_court():
            if isinstance(action, Move):
                defensive_position = team.get_defensive_position(action.player)
                if defensive_position and game.field.distance(
                    action.dest, defensive_position
                ) < game.field.distance(action.src, defensive_position):
                    value = self.importance
            elif isinstance(action, Block) and is_front_row:
                # Solo los jugadores en la fila delantera pueden bloquear
                value = self.importance
        else:
            if isinstance(action, Receive) and not is_front_row:
                # Jugadores en la fila trasera se enfocan en recibir
                value = self.importance
            elif isinstance(action, Dig):
                value = self.importance
            elif isinstance(action, Move):
                anticipated_position = game.predict_ball_landing_position()
                if anticipated_position and game.field.distance(
                    action.dest, anticipated_position
                ) < game.field.distance(action.src, anticipated_position):
                    value = self.importance

        return value

    @staticmethod
    def is_front_row(position: Tuple[int, int], team: str, game: Game) -> bool:
        # Determina si la posición está en la fila delantera
        net_row = game.field.net_row
        if team == T1:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class OffensiveBehavior(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        team = game.t1 if action.team == T1 else game.t2
        current_position = game.get_player_position(action.player, action.team)

        value = 0.0

        is_front_row = self.is_front_row(current_position, action.team, game)

        if game.ball_in_our_court():
            if game.player_has_ball(action.player, action.team):
                if isinstance(action, Set):
                    value = self.importance
                elif isinstance(action, Attack) and is_front_row:
                    # Solo los jugadores en la fila delantera pueden atacar por encima de la red
                    value = self.importance
                elif isinstance(action, Move):
                    attacking_position = team.get_attacking_position(action.player)
                    if attacking_position and game.field.distance(
                        action.dest, attacking_position
                    ) < game.field.distance(action.src, attacking_position):
                        value = self.importance
            else:
                if isinstance(action, Move):
                    support_position = team.get_support_position(action.player)
                    if support_position and game.field.distance(
                        action.dest, support_position
                    ) < game.field.distance(action.src, support_position):
                        value = self.importance
        else:
            if isinstance(action, Serve) and game.is_player_server(action.player):
                value = self.importance

        return value

    @staticmethod
    def is_front_row(position: Tuple[int, int], team: str, game: Game) -> bool:
        net_row = game.field.net_row
        if team == T1:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class AvoidFatigueBehavior(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        # Evaluar acciones que consumen menos energía
        value = 0.0
        effort = 0

        if isinstance(action, Move):
            effort = 1
        elif isinstance(action, Attack):
            effort = 3
        elif isinstance(action, Serve):
            effort = 2
        elif isinstance(action, Block):
            effort = 2
        elif isinstance(action, Dig):
            effort = 2
        elif isinstance(action, Receive):
            effort = 2
        elif isinstance(action, Set):
            effort = 1
        elif isinstance(action, Nothing):
            effort = 0
            value = self.importance  # Hacer nada conserva energía

        if effort > 0 and not isinstance(action, Nothing):
            value = (1 / (effort + 1)) * self.importance

        self.update_importance(action.team, game)
        return value

    def update_importance(self, team: str, game: Game) -> None:
        # Ajustar la importancia según la situación del juego
        self.importance *= 1.01  # Aumentar gradualmente la importancia
        self_team_sets = game.t1_sets if team == T1 else game.t2_sets
        enemy_team_sets = game.t2_sets if team == T1 else game.t1_sets
        # Reducir importancia si estamos perdiendo por mucho
        if enemy_team_sets - self_team_sets > 1:
            self.importance *= 0.9
        # Aumentar importancia en situaciones críticas
        if (
            game.current_set == game.max_sets
            and max(game.t1_score, game.t2_score) >= 20
        ):
            self.importance *= 0.75  # Conservar energía para puntos críticos
