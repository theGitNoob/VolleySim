from random import choice
from typing import Callable

from Tools.enum import dict_t1
from .actions import *
from .bdiagent import BdiAgent
from .behavior import Behavior, RandomBehavior, Defensive, ReturnToPosition, Ofensive
from .fuzzy_rules import DefensivePositionFuzzySystem, OffensivePositionFuzzySystem
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

    def select_action(
            self,
            possible_actions: Callable[[Game], List[Action]],
            simulator: SimulatorAgent,
    ) -> Action:
        team = possible_actions(simulator.game)[0].team
        agent = BdiAgent(simulator.game)
        return agent.select_action(possible_actions, team)


class DefensorStrategy(BehaviorStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.behaviors: List[Behavior] = [Defensive(importance=1.8),
                                          ReturnToPosition(importance=0.5),
                                          Ofensive(importance=0.2),
                                          RandomBehavior(importance=0.1)]


class OfensorStrategy(BehaviorStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.behaviors: List[Behavior] = [Ofensive(importance=1.8),
                                          ReturnToPosition(importance=0.5),
                                          Defensive(importance=0.2),
                                          RandomBehavior(importance=0.1)]


class RandomStrategy(BehaviorStrategy, PlayerStrategy):
    def __init__(self):
        super().__init__()
        self.behaviors: List[Behavior] = [RandomBehavior()]

    def select_action(
            self,
            possible_actions: Callable[[Game], List[Action]],
            simulator: SimulatorAgent,
    ) -> Action:
        return choice(possible_actions(simulator.game))


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

        # print(f'{"T1" if team == T1 else "T2"}-{player} player is thinking')

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
    def __init__(self):
        self.defensive_fuzzy = DefensivePositionFuzzySystem()
        self.offensive_fuzzy = OffensivePositionFuzzySystem()

    def eval(self, game: Game, team: str) -> float:
        opponent_team = T1 if team == T2 else T2

        score_diff = game.get_team_score(team) - game.get_team_score(opponent_team)
        set_diff = game.get_team_sets(team) - game.get_team_sets(opponent_team)
        ball_possession = 1 if game.ball_possession_team == team else -1
        touches_left = 3 - game.touches[team]
        ball_on_our_side = 1 if game.is_ball_on_our_side(team) else -1

        avg_defensive_score = self.avg_defensive_position(self, game, team) / 100  # Normalizar entre 0 y 1
        avg_offensive_score = self.avg_offensive_position(self, game, team) / 100  # Normalizar entre 0 y 1

        value = (
                set_diff * 100000
                + score_diff * 100
                + ball_possession * 50
                + touches_left * 20
                + ball_on_our_side * 30
                + avg_defensive_score * 100
                + avg_offensive_score * 100
        )

        return value

    @staticmethod
    def avg_defensive_position(self, game: Game, team: str) -> float:
        avg = 0
        count = 0
        for player in game.get_players(team):
            player_position = game.field.find_player(player, team)
            ideal_position = dict_t1[player_position.position] if team == T1 else player_position.position
            player_position = player_position.row, player_position.col
            player_role = game.t1.get_player_role(player) if team == T1 else game.t2.get_player_role(player)
            ball_position = game.field.find_ball()
            ball_position = ball_position.row, ball_position.col
            distance_to_position = game.field.distance(player_position, ideal_position)
            distance_to_ball = game.field.distance(player_position, ball_position)

            defensive_score = self.defensive_fuzzy.evaluate(distance_to_position, distance_to_ball, player_role)

            avg += defensive_score
            count += 1

        return avg / count if count > 0 else 0

    @staticmethod
    def avg_offensive_position(self, game: Game, team: str) -> float:
        avg = 0
        count = 0
        for player in game.get_players(team):
            player_position = game.field.find_player(player, team)
            ideal_position = dict_t1[player_position.position] if team == T1 else player_position.position
            player_position = player_position.row, player_position.col
            player_role = game.t1.get_player_role(player) if team == T1 else game.t2.get_player_role(player)
            ball_position = game.field.find_ball()
            ball_position = ball_position.row, ball_position.col
            distance_to_position = game.field.distance(player_position, ideal_position)
            distance_to_ball = game.field.distance(player_position, ball_position)

            defensive_score = self.defensive_fuzzy.evaluate(distance_to_position, distance_to_ball, player_role)

            avg += defensive_score
            count += 1

        return avg / count if count > 0 else 0
