from random import choice
from typing import Callable

from .actions import *
from .behavior import (Behavior, Defensive, Ofensive, RandomBehavior,
                       ReturnToPosition)
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
        self.strategies = {"defensor": DefensorStrategy(), "ofensor": OfensorStrategy()}

    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        actions = possible_actions(simulator.game)
        game = simulator.game
        player = actions[0].player
        team = actions[0].team
        ball_in_our_court = simulator.game.ball_in_our_court(team)

        # Obtener el rol del jugador
        if team == T1:
            player_role = game.t1.get_player_role(player)
        else:
            player_role = game.t2.get_player_role(player)

        if ball_in_our_court:
            if Serve in actions:
                return self.strategies["ofensor"].select_action_behavior(
                    actions, simulator
                )
            if player_role == "O":
                return self.strategies["ofensor"].select_action_behavior(
                    actions, simulator
                )
            else:
                return self.strategies["defensor"].select_action_behavior(
                    actions, simulator
                )
        else:
            return self.strategies["defensor"].select_action_behavior(
                actions, simulator
            )


class DefensorStrategy(BehaviorStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.behaviors: List[Behavior] = [
            Defensive(importance=1.8),
            ReturnToPosition(importance=0.5),
            Ofensive(importance=0.2),
            RandomBehavior(importance=0.1),
        ]


class OfensorStrategy(BehaviorStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.behaviors: List[Behavior] = [
            Ofensive(importance=1.8),
            ReturnToPosition(importance=0.5),
            Defensive(importance=0.2),
            RandomBehavior(importance=0.1),
        ]


class RandomStrategy(BehaviorStrategy, PlayerStrategy):
    def __init__(self):
        super().__init__()
        self.behaviors: List[Behavior] = [RandomBehavior()]

    def select_action(
        self,
        possible_actions: Callable[[Game], List[Action]],
        simulator: SimulatorAgent,
    ) -> Action:
        # TODO: check if this is correct
        # return a random action in all the possible actions
        return choice(possible_actions(simulator.game))
        # return self.select_action_behavior(possible_actions(simulator.game), simulator)


MIN = -10000000000
CANT_SIMULATIONS = 1


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

        depth = 1

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
    ) -> Tuple[float, Action | None]:
        if depth == 0 or simulator.game.is_finish():
            return self.evaluation(simulator.game, actions[0].team)

        best, best_action = MIN, None

        for action in actions:
            len_stack = len(simulator.dispatch().stack)

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
                simulator.dispatch().rollback()

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

        set_diff = game.get_team_sets(team) - game.get_team_score(opponent_team)

        # Posesión de la pelota
        ball_possession = 1 if game.ball_possession_team == team else -1

        # Toques restantes
        touches_left = 3 - game.touches[team]

        # Ubicación de la pelota
        ball_on_our_side = 1 if game.is_ball_on_our_side(team) else -1

        # Valor total
        value = (
            set_diff * 100000
            + score_diff * 100
            + ball_possession * 50
            + touches_left * 20
            + ball_on_our_side * 30
        )

        return value
