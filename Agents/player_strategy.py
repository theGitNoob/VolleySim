from random import choice
from typing import Callable

from Tools.enum import PlayerRole

from .actions import *
from .behavior import Behavior, RandomBehavior
from .simulator_agent import SimulatorAgent


class PlayerStrategy(ABC):
    @abstractmethod
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        pass


class BehaviorStrategy(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.behaviors: List[Behavior] = []

    def select_action_behavior(
        self, actions: List[Action], simulator: SimulatorAgent
    ) -> Action:
        return max(
            actions,
            key=lambda a: sum([b.eval(a, simulator.game) for b in self.behaviors]),
        )


class VolleyballStrategy(PlayerStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.strategies = {
            PlayerRole.SETTER: SetterStrategy(),
            PlayerRole.OUTSIDE_HITTER: OutsideHitterStrategy(),
            PlayerRole.OPPOSITE_HITTER: OppositeStrategy(),
            PlayerRole.MIDDLE_BLOCKER: MiddleBlockerStrategy(),
            PlayerRole.LIBERO: LiberoStrategy(),
        }

    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        # Obtener el rol del jugador
        if team == T1:
            player_role = game.t1.get_player_role(player)
        else:
            player_role = game.t2.get_player_role(player)

        # Obtener la estrategia correspondiente al rol
        strategy = self.strategies.get(player_role, None)
        if strategy:
            return strategy.select_action(possible_actions, simulator)
        else:
            return choice(actions)


class OppositeStrategy(PlayerStrategy):
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        # Obtener la posición actual del jugador
        current_position = game.get_player_position(player, team)
        is_front_row = self.is_front_row(current_position, team, game)

        # Si está en la fila delantera, priorizar ataques
        if is_front_row:
            attack_actions = [
                action for action in actions if isinstance(action, Attack)
            ]
            defensive_actions = [
                action for action in actions if isinstance(action, Block)
            ]
            if attack_actions:
                return max(
                    attack_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
            elif defensive_actions:
                return max(
                    defensive_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
        else:
            # Si está en la fila trasera, priorizar acciones defensivas
            attack_actions = [
                action for action in actions if isinstance(action, Attack)
            ]
            defensive_actions = [
                action
                for action in actions
                if isinstance(action, Receive) or isinstance(action, Dig)
            ]
            if defensive_actions:
                return max(
                    defensive_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
            elif attack_actions:
                return max(
                    attack_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )

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
        if team == T1:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class LiberoStrategy(PlayerStrategy):
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones defensivas
        defensive_actions = [
            action
            for action in actions
            if isinstance(action, Receive) or isinstance(action, Dig)
        ]
        if defensive_actions:
            return max(
                defensive_actions,
                key=lambda action: self.evaluate_action(action, simulator.game),
            )
        # Si no hay acciones defensivas disponibles, elegir la mejor acción disponible
        return self.choose_best_action(actions, simulator.game)

    def evaluate_action(self, action: Action, game: Game) -> float:
        return 1.0

    def choose_best_action(self, actions: List[Action], game: Game) -> Action:
        return actions[0]


class SetterStrategy(PlayerStrategy):
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones de colocación
        set_actions = [action for action in actions if isinstance(action, Set)]
        if set_actions:
            return max(
                set_actions,
                key=lambda action: self.evaluate_action(action, simulator.game),
            )
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
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team

        current_position = game.get_player_position(player, team)
        is_front_row = self.is_front_row(current_position, team, game)

        # Si está en la fila delantera, priorizar ataques
        if is_front_row:
            attack_actions = [
                action for action in actions if isinstance(action, Attack)
            ]
            defensive_actions = [
                action
                for action in actions
                if isinstance(action, Block)
                or isinstance(action, Dig)
                or isinstance(action, Receive)
            ]
            if attack_actions:
                return max(
                    attack_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
            elif defensive_actions:
                return max(
                    defensive_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
        else:
            # Si está en la fila trasera, priorizar acciones defensivas
            attack_actions = [
                action for action in actions if isinstance(action, Attack)
            ]
            defensive_actions = [
                action
                for action in actions
                if isinstance(action, Receive) or isinstance(action, Dig)
            ]
            if defensive_actions:
                return max(
                    defensive_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )
            elif attack_actions:
                return max(
                    attack_actions,
                    key=lambda action: self.evaluate_action(action, game),
                )

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
        if team == T1:
            return net_row - 3 <= position[0] < net_row
        else:
            return net_row < position[0] <= net_row + 3


class MiddleBlockerStrategy(PlayerStrategy):
    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        # Priorizar acciones de bloqueo y ataque rápido
        block_actions = [action for action in actions if isinstance(action, Block)]
        quick_attack_actions = [
            action
            for action in actions
            if isinstance(action, Attack) and action.is_quick_attack
        ]
        if block_actions:
            return max(
                block_actions,
                key=lambda action: self.evaluate_action(action, simulator.game),
            )
        elif quick_attack_actions:
            return max(
                quick_attack_actions,
                key=lambda action: self.evaluate_action(action, simulator.game),
            )
        # Si no hay acciones de bloqueo o ataque rápido, elegir la mejor acción disponible
        return self.choose_best_action(actions, simulator.game)

    def evaluate_action(self, action: Action, game: Game) -> float:
        return 1.0

    def choose_best_action(self, actions: List[Action], game: Game) -> Action:
        return actions[0]


class RandomStrategy(BehaviorStrategy, PlayerStrategy):
    def __init__(self):
        super().__init__()
        self.behaviors: List[Behavior] = [RandomBehavior()]

    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        return self.select_action_behavior(possible_actions(simulator.game), simulator)


MIN = -10000000000
CANT_SIMULATIONS = 1


class PlayerStrategy(ABC):
    @abstractmethod
    def play(self, simulator: SimulatorAgent) -> Action:
        pass


class MinimaxStrategy(PlayerStrategy):
    def __init__(self):
        super().__init__()
        self.evaluator = GameEvaluator()

    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)

        team = actions[0].team
        player = actions[0].player
        print(f'{"T1" if team == T1 else "T2"}-{player} player is thinking')

        depth = 2

        action = self.best_function(actions, possible_actions, simulator, depth, True)[
            1
        ]

        return action

    def best_function(
        self,
        actions: List[Action],
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
        depth: int,
        first: bool = False,
    ) -> Tuple[int, Action | None]:
        if depth == 0 or simulator.game.is_finish():
            return self.evaluation(simulator.game, simulator.team)

        best, best_action = MIN, None

        for action in actions:
            len_stack = len(simulator.dispatch().stack)

            str(simulator.game.field)

            simulator.dispatch().dispatch(action)

            for _ in range(CANT_SIMULATIONS):
                if first:
                    simulator.simulate_current()
                else:
                    simulator.simulate()

                r, _ = self.best_function(
                    possible_actions(simulator.game),
                    possible_actions,
                    simulator,
                    depth - 1,
                )

                if r > best:
                    best = r
                    best_action = action

                if first:
                    simulator.reset_current()
                    simulator.dispatch().dispatch(action)
                else:
                    simulator.reset()

            while len(simulator.dispatch().stack) != len_stack:
                simulator.dispatch().reset()

        return best, best_action

    def evaluation(self, game: Game, team: str) -> Tuple[float, Action | None]:
        return self.evaluator.eval(game, team), None


class GameEvaluator:
    def eval(self, game: Game, team: str) -> float:
        """
        Evalúa el estado actual del juego desde la perspectiva del equipo especificado.
        """
        opponent_team = T1 if team == T2 else T2

        # Diferencia de puntos
        score_diff = game.get_team_score(team) - game.get_team_score(opponent_team)

        # Posesión de la pelota
        ball_possession = 1 if game.ball_possession_team == team else -1

        # Toques restantes
        touches_left = 3 - game.touches[team]

        # Ubicación de la pelota
        ball_on_our_side = 1 if game.is_ball_on_our_side(team) else -1

        # Valor total
        value = (
            score_diff * 100
            + ball_possession * 50
            + touches_left * 20
            + ball_on_our_side * 30
        )

        return value
