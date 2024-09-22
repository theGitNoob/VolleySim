# manager_action_strategy.py

from abc import ABC, abstractmethod
from typing import List, Tuple
from random import choice

from .actions import Action, Substitution, Timeout, ManagerNothing
from .fuzzy_rules import fuzzy_defensive_position, fuzzy_offensive_position
from .simulator_agent import SimulatorAgent
from ..Tools.game import Game
from ..Tools.field import GridField
from .actions import *
from .manager_line_up_strategy import possible_line_ups
from ..Tools.enum import HOME, AWAY

# Definición de roles específicos del voleibol
SETTER = 'SETTER'
HITTER = 'HITTER'
MIDDLE_BLOCKER = 'MIDDLE_BLOCKER'
LIBERO = 'LIBERO'
OPPOSITE = 'OPPOSITE'

MIN = float('-inf')
MAX = float('inf')

CANT_SIMULATIONS = 1  # Número de simulaciones a realizar


def possible_substitutions(game: Game, team: str) -> List[Action]:
    possibles = []

    team_data = game.home if team == HOME else game.away

    max_substitutions_per_set = 6  # Máximo de sustituciones por set en voleibol
    if len(team_data.substitution_history) >= max_substitutions_per_set:
        return []

    # Iterar sobre los jugadores en cancha
    for position_number, player_info in team_data.line_up.line_up.items():
        player_on_court = player_info.player

        # Evitar sustituir al líbero
        if player_info.player_role == LIBERO:
            continue

        # Generar posibles sustituciones con jugadores en el banco
        for bench_player in team_data.on_bench:
            # Evitar sustituir a un jugador que ya entró por el mismo jugador en el set
            if any(sub for sub in team_data.substitution_history if sub['in'] == bench_player and sub['out'] == player_on_court):
                continue

            substitution_action = Substitution(player_on_court, bench_player, team, game)
            possibles.append(substitution_action)

    return possibles


def possible_actions(game: Game, team: str) -> List[Action]:
    substitution_options = possible_substitutions(game, team)

    # Incluir opciones de tiempo muerto
    timeout_options = []
    if game.can_call_timeout(team):
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
        print(f'El entrenador del equipo {"local" if team == HOME else "visitante"} está pensando...')

        actions = possible_actions(simulator.game, team)
        if not actions:
            return ManagerNothing(team, simulator.game)

        results = {i: 0 for i in range(len(actions))}

        for i, action in enumerate(actions):
            for _ in range(CANT_SIMULATIONS):
                len_stack = len(simulator.dispatch().stack)

                simulator.dispatch().dispatch(action)
                simulator.simulate_current()
                simulator.simulate()

                # Evaluar el resultado
                value = ManagerGameEvaluator().eval(simulator.game, team)
                results[i] += value

                # Resetear el estado del simulador
                simulator.reset()
                simulator.reset_current()
                while len(simulator.dispatch().stack) != len_stack:
                    simulator.dispatch().reset()

        # Elegir la acción con el mayor valor acumulado
        best_action_index = max(results, key=results.get)
        return actions[best_action_index]


class ActionMiniMaxStrategy(ManagerActionStrategy):
    def action(self, team: str, simulator: SimulatorAgent) -> Action:
        print(f'El entrenador del equipo {"local" if team == HOME else "visitante"} está pensando...')

        depth = 2  # Profundidad del árbol de decisión

        simulator.simulate_current()
        if team == HOME:
            value, action = self.maximize(simulator, depth, MIN, MAX, team)
        else:
            value, action = self.minimize(simulator, depth, MIN, MAX, team)
        simulator.reset_current()

        return action if action else ManagerNothing(team, simulator.game)

    def maximize(self, simulator: SimulatorAgent, depth: int, alpha: float, beta: float, team: str) -> Tuple[float, Action]:
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

            simulator.dispatch().reset()
            while len(simulator.dispatch().stack) != len_stack:
                simulator.dispatch().reset()

            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        return max_eval, best_action

    def minimize(self, simulator: SimulatorAgent, depth: int, alpha: float, beta: float, team: str) -> Tuple[float, Action]:
        if depth == 0 or simulator.game.is_finish():
            return ManagerGameEvaluator().eval(simulator.game, team), None

        min_eval = MAX
        best_action = None

        opponent_team = HOME if team == AWAY else AWAY
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

            simulator.dispatch().reset()
            while len(simulator.dispatch().stack) != len_stack:
                simulator.dispatch().reset()

            beta = min(beta, eval)
            if beta <= alpha:
                break

        return min_eval, best_action


class ManagerGameEvaluator:
    def eval(self, game: Game, team: str) -> float:
        # Evaluar el estado del juego desde la perspectiva del entrenador
        # Considerar la puntuación, niveles de fatiga y otros factores

        # Diferencia de puntuación
        score_diff = (game.home_score - game.away_score) if team == HOME else (game.away_score - game.home_score)

        # Penalización por fatiga
        fatigue_penalty = self.calculate_fatigue_penalty(game, team)

        # Evaluación total
        return score_diff - fatigue_penalty

    def calculate_fatigue_penalty(self, game: Game, team: str) -> float:
        team_data = game.home if team == HOME else game.away
        total_stamina = sum(player.stamina for player in team_data.data.values())
        average_stamina = total_stamina / len(team_data.data)

        # Retornar una penalización basada en la fatiga (menor resistencia implica mayor penalización)
        return (100 - average_stamina) / 10  # Ajustar el divisor según sea necesario
