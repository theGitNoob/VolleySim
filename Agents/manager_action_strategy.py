from abc import ABC, abstractmethod
from random import choice
from typing import List

from Tools.enum import T1
from Tools.game import Game
from .actions import (Action, ManagerCelebrate, ManagerNothing, Substitution,
                      Timeout)
from .simulator_agent import SimulatorAgent

MIN = float("-inf")
MAX = float("inf")

CANT_SIMULATIONS = 1


def possible_substitutions(game: Game, team: str) -> List[Action]:
    possibles = []

    team_data = game.t1 if team == T1 else game.t2

    max_substitutions_per_set = 2
    if len(team_data.substitution_history) >= max_substitutions_per_set:
        return []

    for position_number, player_info in team_data.line_up.line_up.items():
        player_on_court = player_info.player

        for bench_player in team_data.on_bench:
            if any(
                    sub
                    for sub in team_data.substitution_history
                    if sub[1] == bench_player and sub[0] == player_on_court
            ):
                continue

            if (
                    team_data.data[player_on_court].position
                    != team_data.data[bench_player].position
            ):
                continue

            substitution_action = Substitution(
                player_on_court, bench_player, team, game
            )
            possibles.append(substitution_action)

    return possibles


def possible_actions(game: Game, team: str) -> List[Action]:
    substitution_options = possible_substitutions(game, team)

    celebration_options = []
    if game.ball_possession_team == team:
        celebration_options.append(ManagerCelebrate(team, game))

    timeout_options = []
    if game.can_call_time_out(team):
        timeout_options.append(Timeout(team, game))

    return substitution_options + timeout_options + [ManagerNothing(team, game)]


class ManagerActionStrategy(ABC):
    @abstractmethod
    def action(self, team: str, simulator: SimulatorAgent) -> Action:
        pass


class ActionRandomStrategy(ManagerActionStrategy):
    def action(self, team: str, simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game, team)
        return choice(actions) if actions else ManagerNothing(team, simulator.game)


class ActionSimulateStrategy(ManagerActionStrategy):

    def action(self, team: str, simulator: SimulatorAgent) -> Action:

        game = simulator.game
        team_score = game.t1_score if team == T1 else game.t2_score
        enemy_score = game.t2_score if team == T1 else game.t1_score
        actions = possible_actions(simulator.game, team)
        points_history = game.points_history
        last_team_points, last_enemy_points = self.get_continues_points(game, team)

        if points_history[len(points_history) - 1]["set"] not in [2, 4]:
            return ManagerNothing(team, game)

        if last_team_points != 0:
            if 0 <= team_score - enemy_score < 3:
                return ManagerNothing(team, game)
            elif team_score - enemy_score >= 3:
                return ManagerCelebrate(team, game)
        elif (
                1 < last_enemy_points - last_team_points <= 3
                and 1 < enemy_score - team_score <= 3
        ):
            return Timeout(team, game)

        if last_team_points - last_enemy_points > 3:
            return ManagerCelebrate(team, game)

        if enemy_score - team_score < 3:
            return ManagerNothing(team, game)

        max_errors = 0
        player_error = None
        for player in game.t1.on_field if team == T1 else game.t2.on_field:
            if (
                    game.t1.data[player].errors > max_errors
                    if team == T1
                    else game.t2.data[player].errors > max_errors
            ):
                max_errors = (
                    game.t1.data[player].errors
                    if team == T1
                    else game.t2.data[player].errors
                )
                player_error = player

        value = 0
        action_selected = None
        for action in actions:
            if isinstance(action, Substitution) and team_score < enemy_score:
                if action.player_out == player_error:
                    player_in_role = (
                        action.game.t1.get_player_role(action.player_in)
                        if team == T1
                        else action.game.t2.get_player_role(action.player_in)
                    )
                    player_in_data = (
                        action.game.t1.data[action.player_in]
                        if team == T1
                        else action.game.t2.data[action.player_in]
                    )
                    if player_in_role == "L":
                        if (
                                player_in_data.p_receive + player_in_data.p_dig
                        ) / 2 > value:
                            value = (
                                            player_in_data.p_receive + player_in_data.p_dig
                                    ) / 2
                            action_selected = action
                    elif player_in_role == "S":
                        if player_in_data.p_set > value:
                            value = player_in_data.p_set
                            action_selected = action
                    elif player_in_role == "O":
                        if player_in_data.p_attack > value:
                            value = player_in_data.p_attack
                            action_selected = action
                    elif player_in_role == "OH":
                        if (
                                player_in_data.p_attack
                                + player_in_data.p_dig
                                + player_in_data.p_receive
                        ) / 3 > value:
                            value = (
                                            player_in_data.p_attack
                                            + player_in_data.p_dig
                                            + player_in_data.p_receive
                                    ) / 3
                            action_selected = action
                    elif player_in_role == "MB":
                        if (
                                player_in_data.p_block + player_in_data.p_attack
                        ) / 2 > value:
                            value = (
                                            player_in_data.p_block + player_in_data.p_attack
                                    ) / 2
                            action_selected = action
        return action_selected if action_selected else ManagerNothing(team, game)

    @staticmethod
    def get_continues_points(game: Game, team: str) -> (int, int):
        team_points = enemy_points = 0
        change_team = change_enemy = False
        game.points_history.reverse()
        for point in game.points_history:
            if point["team"] == team and not change_team:
                team_points += 1
                if enemy_points > 0:
                    change_enemy = True
            elif point["team"] != team and not change_enemy:
                enemy_points += 1
                change_team = True
            else:
                break
        game.points_history.reverse()
        return team_points, enemy_points
