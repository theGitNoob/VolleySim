# behavior.py

import random

from Tools.enum import T1, dict_t1, dict_t2
from Tools.field import GridField
from Tools.game import Game

from .actions import Action, Block, Dig, Move, Nothing, Receive, Serve, Set


class Behavior:
    def __init__(self, importance: float = 1.0) -> None:
        self.importance = importance

    def eval(self, action: Action, game: Game) -> float:
        pass

    def change_importance(self, importance: float) -> None:
        self.importance = importance


class Random(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        return random.random() * self.importance


class ReturnToPosition(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        team = game.t1 if action.team == T1 else game.t2
        line_up_position = team.line_up.get_player_position(action.player)
        line_up_position = (line_up_position.row, line_up_position.col)
        source = action.src
        destination = action.dest

        if action is Move:
            return (
                1
                if game.field.distance(destination, line_up_position)
                < game.field.distance(source, line_up_position)
                else 0
            ) * self.importance
        else:
            return 0


class Defensive(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        source = action.src
        destination = action.dest
        ball_position = game.field.find_ball()
        self_team = action.team
        opponent_team = game.get_opponent_team(self_team)
        player = game.field.find_player(action.player, self_team)

        value = 0

        # Si el equipo tiene la posesión del balón
        if ball_position.team == self_team:
            if isinstance(action, Block):
                neighbor_opponents = 0
                x, y = destination
                dest_grid: GridField = GridField(x, y, -1, False, "")
                for grid in game.field.neighbor_grids(dest_grid, 2):
                    if grid.team == opponent_team:
                        neighbor_opponents += 1
                value += 1 / (neighbor_opponents + 1)
            elif isinstance(action, Receive) or isinstance(action, Dig):
                setter_position = game.role_position("S", self_team)
                distance_to_setter = game.field.distance(
                    destination, (setter_position.row, setter_position.col)
                )
                value += 1 / (distance_to_setter + 1)
            elif isinstance(action, Set):
                opposite_position = game.role_position("O", self_team)
                opposite_hitter_position = game.role_position(
                    "OH", self_team, action.dest
                )
                distance_to_attack = min(
                    game.field.distance(
                        destination, (opposite_position.row, opposite_position.col)
                    ),
                    game.field.distance(
                        destination,
                        (opposite_hitter_position.row, opposite_hitter_position.col),
                    ),
                )
                closest_enemy_distance = game.closest_enemy_distance(
                    destination, self_team
                )
                value += 1 / ((distance_to_attack + closest_enemy_distance) + 1)

        else:
            # El equipo contrario tiene la posesión, acciones defensivas
            if isinstance(action, Move) or isinstance(action, Nothing):
                if player.position == "L":
                    distance = game.field.distance(destination, dict_t1[5])
                    return 1 / (distance + 1)
                elif player.position == "O":
                    if is_front_row(player.row, self_team):
                        distance = game.field.distance(
                            destination, dict_t1[2] if self_team == T1 else dict_t2[2]
                        )
                        return 1 / (distance + 1)
                    else:
                        distance = game.field.distance(
                            destination, dict_t1[1] if self_team == T1 else dict_t2[1]
                        )
                        return 1 / (distance + 1)
                elif player.position == "OH":
                    if is_front_row(player.row, self_team):
                        distance = game.field.distance(
                            destination, dict_t1[4] if self_team == T1 else dict_t2[4]
                        )
                        return 1 / (distance + 1)
                    else:
                        distance = game.field.distance(
                            destination, dict_t1[6] if self_team == T1 else dict_t2[6]
                        )
                        return 1 / (distance + 1)
                elif player.position == "S":
                    distance = game.field.distance(
                        destination, dict_t1[3] if self_team == T1 else dict_t2[3]
                    )
                    return 1 / 10000000 * (distance + 1)
                elif player.position == "MB":
                    distance = game.field.distance(
                        destination, dict_t1[3] if self_team == T1 else dict_t2[3]
                    )
                    return 1 / (distance + 1)

        return value + self.importance


class Ofensive(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        destination = action.dest
        opponent_team = game.get_opponent_team(action.team)
        value = 0

        if isinstance(action, Serve):
            return 1 * self.importance
        elif not isinstance(action, Nothing):
            neighbor_opponents = 0
            x, y = destination
            dest_grid: GridField = GridField(x, y, -1, False, "")
            for grid in game.field.neighbor_grids(dest_grid, 2):
                if grid.team == opponent_team:
                    neighbor_opponents += 1
            value += 1 / (neighbor_opponents + 1)

        return value + self.importance


class RandomBehavior(Behavior):
    def eval(self, action: Action, game: Game) -> float:
        return random.random() * self.importance


def is_front_row(row: int, team: str) -> bool:
    return (team == T1 and 5 < row < 9) or (team != T1 and 9 < row < 13)
