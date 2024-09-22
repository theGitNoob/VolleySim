from .actions import *
from ..Tools.line_up import *
from ..Tools.game import Game
from .simulator_agent import SimulatorAgent
from ..Tools.enum import HOME, AWAY

import random
from typing import List, Callable
from abc import ABC, abstractmethod
from random import choice

CANT_SIMULATIONS = 1


class PlayerStrategy(ABC):
    @abstractmethod
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        pass


class VolleyballStrategy(PlayerStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.strategies = {
            SETTER: SetterStrategy(),
            OUTSIDE_HITTER: OutsideHitterStrategy(),
            OPPOSITE_HITTER: OppositeStrategy(),
            MIDDLE_BLOCKER: MiddleBlockerStrategy(),
            LIBERO: LiberoStrategy()
        }

    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        # Obtener el rol del jugador
        if team == HOME:
            player_role = game.home.get_player_role(player)
        else:
            player_role = game.away.get_player_role(player)

        # Obtener la estrategia correspondiente al rol
        strategy = self.strategies.get(player_role, None)
        if strategy:
            return strategy.select_action(possible_actions, simulator)
        else:
            return choice(actions)


class OppositeStrategy(PlayerStrategy):
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        # Obtener la posición actual del jugador
        current_position = game.get_player_position(player, team)
        is_front_row = self.is_front_row(current_position, team, game)

        # Si está en la fila delantera, priorizar ataques
        if is_front_row:
            attack_actions = [action for action in actions if isinstance(action, Attack)]
            defensive_actions = [action for action in actions if isinstance(action, Block)]
            if attack_actions:
                return max(attack_actions, key=lambda action: self.evaluate_action(action, game))
            elif defensive_actions:
                return max(defensive_actions, key=lambda action: self.evaluate_action(action, game))
        else:
            # Si está en la fila trasera, priorizar acciones defensivas
            attack_actions = [action for action in actions if isinstance(action, Attack)]
            defensive_actions = [action for action in actions if isinstance(action, Receive) or isinstance(action, Dig)]
            if defensive_actions:
                return max(defensive_actions, key=lambda action: self.evaluate_action(action, game))
            elif attack_actions:
                return max(attack_actions, key=lambda action: self.evaluate_action(action, game))

        return self.choose_best_action(actions, game)

    @staticmethod
    def choose_best_action(actions: List[Action], game: Game) -> Action:
        return actions[0]

    @staticmethod
    def evaluate_action(action: Action, game: Game) -> float:
        return 1.0

    @staticmethod
    def is_front_row(position: Tuple[int, int], team: str, game: Game) -> bool:
        # Determina si el jugador está en la fila delantera
        net_row = game.field.net_row
        if team == HOME:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class LiberoStrategy(PlayerStrategy):
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones defensivas
        defensive_actions = [action for action in actions if isinstance(action, Receive) or isinstance(action, Dig)]
        if defensive_actions:
            return max(defensive_actions, key=lambda action: self.evaluate_action(action, simulator.game))
        # Si no hay acciones defensivas disponibles, elegir la mejor acción disponible
        return self.choose_best_action(actions, simulator.game)

    def evaluate_action(self, action: Action, game: Game) -> float:
        return 1.0

    def choose_best_action(self, actions: List[Action], game: Game) -> Action:
        return actions[0]


class SetterStrategy(PlayerStrategy):
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones de colocación
        set_actions = [action for action in actions if isinstance(action, Set)]
        if set_actions:
            return max(set_actions, key=lambda action: self.evaluate_action(action, simulator.game))
        # Si no hay acciones de colocación, elegir la mejor acción disponible
        return self.choose_best_action(actions, simulator.game)

    def evaluate_action(self, action: Action, game: Game) -> float:
        # Evaluar la acción en función de su impacto esperado
        # Aquí puedes añadir lógica específica para valorar cada acción
        return 1.0  # Valor por defecto

    def choose_best_action(self, actions: List[Action], game: Game) -> Action:
        # Implementar lógica para elegir la mejor acción disponible
        return actions[0]  # Por defecto, devuelve la primera acción


class OutsideHitterStrategy(PlayerStrategy):
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        current_position = game.get_player_position(player, team)
        is_front_row = self.is_front_row(current_position, team, game)

        # Si está en la fila delantera, priorizar ataques
        if is_front_row:
            attack_actions = [action for action in actions if isinstance(action, Attack)]
            defensive_actions = [action for action in actions if isinstance(action, Block)
                                 or isinstance(action, Dig) or isinstance(action, Receive)]
            if attack_actions:
                return max(attack_actions, key=lambda action: self.evaluate_action(action, game))
            elif defensive_actions:
                return max(defensive_actions, key=lambda action: self.evaluate_action(action, game))
        else:
            # Si está en la fila trasera, priorizar acciones defensivas
            attack_actions = [action for action in actions if isinstance(action, Attack)]
            defensive_actions = [action for action in actions if isinstance(action, Receive) or isinstance(action, Dig)]
            if defensive_actions:
                return max(defensive_actions, key=lambda action: self.evaluate_action(action, game))
            elif attack_actions:
                return max(attack_actions, key=lambda action: self.evaluate_action(action, game))

        return self.choose_best_action(actions, game)

    @staticmethod
    def choose_best_action(actions: List[Action], game: Game) -> Action:
        return actions[0]

    @staticmethod
    def evaluate_action(action: Action, game: Game) -> float:
        return 1.0

    @staticmethod
    def is_front_row(position: Tuple[int, int], team: str, game: Game) -> bool:
        # Determina si el jugador está en la fila delantera
        net_row = game.field.net_row
        if team == HOME:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class MiddleBlockerStrategy(PlayerStrategy):
    def select_action(self, possible_actions: Callable[[Game], List[Action]], simulator: SimulatorAgent) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones de bloqueo y ataque rápido
        block_actions = [action for action in actions if isinstance(action, Block)]
        quick_attack_actions = [action for action in actions if isinstance(action, Attack) and action.is_quick_attack]
        if block_actions:
            return max(block_actions, key=lambda action: self.evaluate_action(action, simulator.game))
        elif quick_attack_actions:
            return max(quick_attack_actions, key=lambda action: self.evaluate_action(action, simulator.game))
        # Si no hay acciones de bloqueo o ataque rápido, elegir la mejor acción disponible
        return self.choose_best_action(actions, simulator.game)

    def evaluate_action(self, action: Action, game: Game) -> float:
        return 1.0

    def choose_best_action(self, actions: List[Action], game: Game) -> Action:
        return actions[0]

