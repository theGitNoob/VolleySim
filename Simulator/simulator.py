# simulator.py
from typing import Generator, List, Set, Tuple

from prettytable import PrettyTable

from Agents.actions import Dispatch, Move, Nothing
from Agents.manager_action_strategy import (ActionSimulateStrategy)
from Agents.manager_agent import Manager
from Agents.simulator_agent import SimulatorAgent
from Agents.team import TeamAgent
from Tools.data import TeamData
from Tools.enum import T1, T2
from Tools.game import Game
from Tools.utils import coin_toss

# Ajuste de constantes para el voleibol
CANT_RALLIES = 180  # Número máximo de rallies a simular
INTERVAL_MANAGER = (
    1  # Intervalo para decisiones del entrenador (sustituciones, tiempos muertos, etc.)
)


class VolleyballSimulation:
    def __init__(
        self, team1: Tuple[TeamAgent, TeamData], team2: Tuple[TeamAgent, TeamData]
    ) -> None:

        self.t1: TeamAgent = team1[0]
        self.t2: TeamAgent = team2[0]
        self.game: Game = Game(team1[1], team2[1], CANT_RALLIES)

    def simulate(self) -> Generator[str, None, None]:
        simulator = Simulator(self.t1, self.t2, self.game)
        simulator.start_match()

        field_str = str(self.game.field)
        statistics = self.game_statistics()

        yield field_str + "\n" + statistics

        while not self.game.is_finish():
            simulator.simulate_rally(set([]))
            field_str = str(self.game.field)
            statistics = self.game_statistics()
            yield field_str + "\n" + statistics
            # sleep(1)

    def simulate_and_save(self):
        simulator = Simulator(self.t1, self.t2, self.game)
        simulator.start_match()

        while not self.game.is_finish():
            simulator.simulate_rally(set([]))

        return simulator.game.to_json()

    def game_statistics(self) -> str:

        nh = self.t1.name
        na = self.t2.name

        sh = self.game.t1_sets
        sa = self.game.t2_sets
        ph = self.game.t1_score
        pa = self.game.t2_score

        table = PrettyTable()
        table.field_names = ["Team", "Sets Ganados", "Puntos en Set Actual"]
        table.add_row([nh, sh, ph])
        table.add_row([na, sa, pa])
        return table.get_string()


class Simulator:
    def __init__(self, team1: TeamAgent, team2: TeamAgent, game: Game) -> None:
        self.team1: TeamAgent = team1
        self.team2: TeamAgent = team2
        self.game: Game = game
        self.stack: List[int] = []
        self.dispatch = Dispatch(
            self.game
        )  # Ahora Dispatch recibe la instancia de Game

    def start_match(self):
        self.game.instance = 0

        t1_lineup = self.team1.manager.get_line_up(SimulatorLineUpManager(self))
        t2_lineup = self.team2.manager.get_line_up(SimulatorLineUpManager(self))

        self.game.conf_line_ups(t1_lineup, t2_lineup)

        # Determinar equipo que sirve primero
        if coin_toss():
            self.game.serving_team = T1
            self.game.ball_possession_team = T1
            ball_position = self.game.field.find_ball()
            ball_position = (ball_position.row, ball_position.col)
            print("Sirve T1")
            self.game.field.move_ball(ball_position, (2, 2))
        else:
            self.game.serving_team = T2
            self.game.ball_possession_team = T2
            ball_position = self.game.field.find_ball()
            ball_position = (ball_position.row, ball_position.col)
            print("Sirve T2")
            self.game.field.move_ball(ball_position, (17, 6))

        self.game.start_rally()
        self.game.instance = 1

    def simulate_rally(
        self,
        mask: Set[Tuple[int, str]],
        heuristic_manager: bool = False,
        heuristic_player: bool = False,
    ):
        self.stack.append(len(self.dispatch.stack))

        self.game.has_ball_landed = True
        self.game.rally_over = False

        current_team = self.game.ball_possession_team
        other_team = T1 if current_team == T2 else T2

        c_team: [TeamData] = self.game.t1 if current_team == T1 else self.game.t2
        o_team: [TeamData] = self.game.t2 if current_team == T1 else self.game.t1

        current_team_actions = []
        other_team_actions = []
        ball_touched = False

        current_team_players = self.team1 if current_team == T1 else self.team2
        other_team_players = self.team2 if current_team == T1 else self.team1
        current_team_players = current_team_players.players
        other_team_players = other_team_players.players

        for player in c_team.on_field:
            if (player, current_team) in mask:
                continue
            mask.add((player, other_team))
            sim = self.get_player_simulator(current_team, player, mask)

            player_action = (
                current_team_players[player].play(sim)
                if not heuristic_player
                else current_team_players[player].play_heuristic(sim)
            )
            current_team_actions.append(player_action)

        for player in o_team.on_field:

            if (player, other_team) in mask:
                continue
            mask.add((player, other_team))
            sim = self.get_player_simulator(current_team, player, mask)

            player_action = (
                other_team_players[player].play(sim)
                if not heuristic_player
                else other_team_players[player].play_heuristic(sim)
            )

            other_team_actions.append(player_action)

        for action in current_team_actions:
            if ball_touched and not isinstance(action, Move):
                action = Nothing(action.player, action.team, self.game)

            self.dispatch.dispatch(action)
            if action.__class__.__name__ in (
                "Serve",
                "Attack",
                "Block",
                "Receive",
                "Dig",
                "Set",
            ):
                ball_touched = True

        for action in other_team_actions:
            if ball_touched and not isinstance(action, Move):
                action = Nothing(action.player, action.team, self.game)

            self.dispatch.dispatch(action)
            if action.__class__.__name__ in (
                "Serve",
                "Attack",
                "Block",
                "Receive",
                "Dig",
                "Set",
            ):
                ball_touched = True

        # chequear si hubo punto o la pelota tocó el suelo
        if self.game.has_ball_landed:
            ball_position = self.game.field.find_ball()
            scorer_team = T1 if ball_position.team == T2 else T2
            self.game.score_point(scorer_team)
        elif self.game.rally_over:
            self.game.score_point(self.game.last_team_touched)

        # Incrementar el contador de instancias (rallies)
        self.game.instance += 1

        # Simular decisiones de los entrenadores
        self.simulate_managers(mask)

    def get_player_action(self, team: str, player_number: int, sim: SimulatorAgent):
        # Obtener la acción que el jugador realizará
        if team == T1:
            return self.team1.players[player_number].play(sim)
        else:
            return self.team2.players[player_number].play(sim)

    def simulate_managers(self, mask: Set[Tuple[int, str]]):
        if self.game.instance % INTERVAL_MANAGER == 0 and self.game.has_ball_landed:
            if (T1, "manager") not in mask:
                mask.add((T1, "manager"))
                sim = self.get_simulator(self.team1.manager, T1, mask)
                action = self.team1.manager.action(sim)
                self.dispatch.dispatch(action)

            if (T2, "manager") not in mask:
                mask.add((T2, "manager"))
                sim = self.get_simulator(self.team2.manager, T2, mask)
                action = self.team2.manager.action(sim)
                self.dispatch.dispatch(action)

    def get_simulator(self, manager: Manager, team: str, mask: Set[Tuple[int, str]]):
        if isinstance(manager.action_strategy, ActionSimulateStrategy):
            return SimulatorActionSimulateManager(self, team, mask)
        return SimulatorRandom(self.game)

    def get_player_simulator(self, team: str, player: int, mask: Set[Tuple[int, str]]):
        return SimulatorActionSimulatePlayer(self, team, player, mask)

    def reset_all(self):
        while self.game.instance != 1:
            self.reset_instance()

    def reset_instance(self):
        self.dispatch.rollback()
        while len(self.dispatch.stack) != self.stack[-1]:
            self.dispatch.rollback()
        self.stack.pop()


class SimulatorRandom(SimulatorAgent):
    def simulate(self):
        pass

    def reset(self):
        pass

    def simulate_current(self):
        pass

    def reset_current(self):
        pass

    def dispatch(self) -> Dispatch:
        pass


class SimulatorLineUpManager(SimulatorAgent):
    def __init__(self, simulator: Simulator):
        super().__init__(simulator.game)
        self.simulator = simulator

    def simulate(self):
        while not self.game.is_finish():
            self.simulator.simulate_rally(set())

    def reset(self):
        self.simulator.reset_all()

    def simulate_current(self):
        pass

    def reset_current(self):
        pass

    def dispatch(self) -> Dispatch:
        return self.simulator.dispatch


class SimulatorActionSimulateManager(SimulatorAgent):
    def __init__(self, simulator: Simulator, team: str, mask: Set[Tuple[int, str]]):
        super().__init__(simulator.game)
        self.team: str = team
        self.simulator: Simulator = simulator
        self.instance: int = simulator.game.instance
        self.stack_len: int = len(simulator.dispatch.stack)
        self.mask: Set[Tuple[int, str]] = mask

    def simulate(self):
        while not self.simulator.game.is_finish():
            self.simulator.simulate_rally(
                set([]), heuristic_manager=True, heuristic_player=True
            )

    def reset(self):
        while self.simulator.game.instance != self.instance + 1:
            self.simulator.reset_instance()

    def simulate_current(self):
        self.simulator.simulate_rally(
            self.mask.copy(), heuristic_manager=True, heuristic_player=True
        )

    def reset_current(self):
        while len(self.simulator.dispatch.stack) != self.stack_len:
            self.simulator.dispatch.rollback()

    def dispatch(self) -> Dispatch:
        return self.simulator.dispatch


class SimulatorActionSimulatePlayer(SimulatorAgent):
    def __init__(
        self, simulator: Simulator, team: str, player: int, mask: Set[Tuple[int, str]]
    ):
        super().__init__(simulator.game)
        self.team: str = team
        self.player: int = player
        self.simulator: Simulator = simulator
        self.instance: int = simulator.game.instance
        self.stack_len: int = len(simulator.dispatch.stack)
        self.mask: Set[Tuple[int, str]] = mask

    def simulate(self):
        self.simulator.simulate_rally(
            {(self.player, self.team)}, heuristic_manager=True, heuristic_player=True
        )

    def reset(self):
        self.simulator.reset_instance()

    def simulate_current(self):
        self.simulator.simulate_rally(
            self.mask.copy(), heuristic_manager=True, heuristic_player=True
        )

    def reset_current(self):
        while len(self.simulator.dispatch.stack) != self.stack_len:
            self.simulator.dispatch.rollback()

    def dispatch(self) -> Dispatch:
        return self.simulator.dispatch


class SimulatorActionMiniMaxManager(SimulatorActionSimulateManager):
    def simulate(self):
        for _ in range(INTERVAL_MANAGER):
            self.simulator.simulate_rally({(T1, "manager"), (T2, "manager")})

    def reset(self):
        for _ in range(INTERVAL_MANAGER):
            self.simulator.reset_instance()

    def simulate_current(self):
        mask = self.mask.copy()
        if self.team == T1:
            mask.add((T2, "manager"))
        else:
            mask.add((T1, "manager"))
        self.simulator.simulate_rally(mask)
