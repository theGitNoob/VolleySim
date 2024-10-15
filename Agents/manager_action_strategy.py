# manager_action_strategy.py

from abc import ABC, abstractmethod
from random import choice
from typing import List, Tuple

from Tools.enum import T1, T2, PlayerRole
from Tools.game import Game

from .actions import (Action, ManagerCelebrate, ManagerNothing, Substitution,
                      Timeout)
from .simulator_agent import SimulatorAgent

MIN = float("-inf")
MAX = float("inf")

CANT_SIMULATIONS = 1  # Número de simulaciones a realizar


def possible_substitutions(game: Game, team: str) -> List[Action]:
    possibles = []

    team_data = game.t1 if team == T1 else game.t2

    max_substitutions_per_set = 2  # Máximo de sustituciones por set en voleibol
    if len(team_data.substitution_history) >= max_substitutions_per_set:
        return []

    # Iterar sobre los jugadores en cancha
    for position_number, player_info in team_data.line_up.line_up.items():
        player_on_court = player_info.player

        # Generar posibles sustituciones con jugadores en el banco
        for bench_player in team_data.on_bench:
            # Evitar sustituir a un jugador que ya entró por el mismo jugador en el set
            if any(
                sub
                for sub in team_data.substitution_history
                if sub[1] == bench_player and sub[0] == player_on_court
            ):
                continue

            # Evitar sustituir a 2 jugadores con distintos roles
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

    # Incluir opciones de tiempo muerto
    timeout_options = []
    if game.can_call_time_out(team):
        timeout_options.append(Timeout(team, game))

    # Incluir acción de no hacer nada
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
        print(
            f"El entrenador del equipo {simulator.game.t1.name if team == T1 else simulator.game.t2.name} está pensando..."
        )

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


class ActionMiniMaxStrategy(ManagerActionStrategy):
    def action(self, team: str, simulator: SimulatorAgent) -> Action:
        print(
            f'El entrenador del equipo {"local" if team == T1 else "visitante"} está pensando...'
        )

        depth = 2  # Profundidad del árbol de decisión

        simulator.simulate_current()
        if team == T1:
            value, action = self.maximize(simulator, depth, MIN, MAX, team)
        else:
            value, action = self.minimize(simulator, depth, MIN, MAX, team)
        simulator.reset_current()

        return action if action else ManagerNothing(team, simulator.game)

    def maximize(
        self,
        simulator: SimulatorAgent,
        depth: int,
        alpha: float,
        beta: float,
        team: str,
    ) -> Tuple[float, Action]:
        if depth == 0 or simulator.game.is_finish():
            return ManagerGameEvaluator().eval(simulator.game, team), None

        max_eval = MIN
        best_action = None

        actions = possible_actions(simulator.game, team)
        if not actions:
            return ManagerGameEvaluator().eval(simulator.game, team), None

        for action in actions:
            len_stack = len(simulator.dispatch().stack)
            simulator.dispatch().dispatch(action)

            eval, _ = self.minimize(simulator, depth - 1, alpha, beta, team)

            if eval > max_eval:
                max_eval = eval
                best_action = action

            simulator.dispatch().rollback()
            while len(simulator.dispatch().stack) != len_stack:
                simulator.dispatch().rollback()

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return max_eval, best_action

    def minimize(
        self,
        simulator: SimulatorAgent,
        depth: int,
        alpha: float,
        beta: float,
        team: str,
    ) -> Tuple[float, Action]:
        if depth == 0 or simulator.game.is_finish():
            return ManagerGameEvaluator().eval(simulator.game, team), None

        min_eval = MAX
        best_action = None

        opponent_team = T1 if team == T2 else T2
        actions = possible_actions(simulator.game, opponent_team)
        if not actions:
            return ManagerGameEvaluator().eval(simulator.game, team), None

        for action in actions:
            len_stack = len(simulator.dispatch().stack)
            simulator.dispatch().dispatch(action)

            eval, _ = self.maximize(simulator, depth - 1, alpha, beta, team)

            if eval < min_eval:
                min_eval = eval
                best_action = action

            simulator.dispatch().rollback()
            while len(simulator.dispatch().stack) != len_stack:
                simulator.dispatch().rollback()

            beta = min(beta, eval)
            if beta <= alpha:
                break

        return min_eval, best_action


class ManagerGameEvaluator:
    def eval(self, game: Game, team: str) -> float:
        # Evaluar el estado del juego desde la perspectiva del entrenador
        # Considerar la puntuación, niveles de fatiga y otros factores

        # Diferencia de puntuación
        score_diff = (
            (game.t1_score - game.t2_score)
            if team == T1
            else (game.t2_score - game.t1_score)
        )
