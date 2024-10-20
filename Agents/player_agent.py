﻿from typing import Generator

from Agents.simulator_agent import SimulatorAgent
from Tools.field import *

from .actions import *
from .player_strategy import PlayerStrategy, VolleyballStrategy


class Player:
    def __init__(self, dorsal: int, team: str, strategy: PlayerStrategy) -> None:
        self.strategy = strategy
        self.heuristic_strategy = VolleyballStrategy()
        self.dorsal = dorsal
        self.team = team

    def possible_actions(self, game: Game) -> List[Action]:
        visible_grids, p_grid = self.get_perceptions(game)
        actions = self.construct_actions(game, visible_grids, p_grid)
        return actions

    def play(self, simulator: SimulatorAgent):
        action = self.strategy.select_action(self.possible_actions, simulator)
        return action

    def play_heuristic(self, simulator: SimulatorAgent):
        action = self.heuristic_strategy.select_action(self.possible_actions, simulator)
        return action

    def get_data(self, game: Game) -> PlayerData:
        if self.team == T1:
            return game.t1.data[self.dorsal]
        else:
            return game.t2.data[self.dorsal]

    def get_perceptions(self, game: Game) -> Tuple[List[GridField], GridField]:
        p_grid: GridField = game.field.find_player(self.dorsal, self.team)
        visible_grids: list[GridField] = [
            grid for row in game.field.grid for grid in row
        ]
        return visible_grids, p_grid

    @staticmethod
    def empty_adjacent_grids(
        visible_grids: List[GridField], p_grid: GridField
    ) -> Generator[GridField, None, None]:
        for g in visible_grids:
            if (
                1 < Field.distance((g.row, g.col), (p_grid.row, p_grid.col)) <= 2
                and g.is_empty()
                and g.team == p_grid.team
            ):
                yield g

    def friendly_grids(
        self, visible_grids: List[GridField]
    ) -> Generator[GridField, None, None]:
        for g in visible_grids:
            if g.team == self.team and not g.is_net:
                yield g

    def enemy_grids(
        self, visible_grids: List[GridField]
    ) -> Generator[GridField, None, None]:
        for g in visible_grids:
            if g.team != self.team and not g.is_net:
                yield g

    def construct_actions(
        self, game: Game, visible_grids: List[GridField], p_grid: GridField
    ) -> List[Action]:
        actions: List[Action] = [Nothing(self.dorsal, self.team, game)]

        ball_src = game.field.find_ball()
        ball_src = (ball_src.row, ball_src.col)

        if game.last_player_touched == self.dorsal and game.general_touches != 0:
            return actions

        if game.is_our_serve(self.team) and game.general_touches == 0:
            if game.is_player_server(self.dorsal):
                actions.pop()
                for grid in self.enemy_grids(visible_grids):
                    dest = (grid.row, grid.col)
                    actions.append(Serve(ball_src, dest, self.dorsal, self.team, game))
            else:
                for grid in self.empty_adjacent_grids(visible_grids, p_grid):
                    dest = (grid.row, grid.col)
                    actions.append(
                        Move(
                            (p_grid.row, p_grid.col), dest, self.dorsal, self.team, game
                        )
                    )

        # La pelota está en nuestro lado
        elif game.is_ball_on_our_side(self.team):
            if game.is_ball_coming_to_player(self.dorsal, self.team):
                if game.last_team_touched != self.team:
                    for grid in self.friendly_grids(visible_grids):
                        actions.append(
                            Dig(
                                ball_src,
                                (grid.row, grid.col),
                                self.dorsal,
                                self.team,
                                game,
                            )
                        )
                    if 5 < game.field.find_player(self.dorsal, self.team).row < 13:
                        for grid in self.enemy_grids(visible_grids):
                            actions.append(
                                Block(
                                    ball_src,
                                    (grid.row, grid.col),
                                    self.dorsal,
                                    self.team,
                                    game,
                                )
                            )
                elif game.touches[self.team] == 1:
                    for grid in self.friendly_grids(visible_grids):
                        actions.append(
                            Set(
                                ball_src,
                                (grid.row, grid.col),
                                self.dorsal,
                                self.team,
                                game,
                            )
                        )
                    for grid in self.enemy_grids(visible_grids):
                        actions.append(
                            Attack(
                                ball_src,
                                (grid.row, grid.col),
                                self.dorsal,
                                self.team,
                                game,
                            )
                        )

                elif game.touches[self.team] == 2:
                    for grid in self.enemy_grids(visible_grids):
                        actions.append(
                            Attack(
                                ball_src,
                                (grid.row, grid.col),
                                self.dorsal,
                                self.team,
                                game,
                            )
                        )

            else:
                for grid in self.empty_adjacent_grids(visible_grids, p_grid):
                    dest = (grid.row, grid.col)
                    actions.append(
                        Move(
                            (p_grid.row, p_grid.col), dest, self.dorsal, self.team, game
                        )
                    )

        return actions
