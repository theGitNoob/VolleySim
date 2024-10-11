# simulator.py
import time
from typing import Generator, List, Set, Tuple

from Agents.actions import Action, Dispatch
from Agents.manager_action_strategy import (ActionMiniMaxStrategy,
                                            ActionSimulateStrategy)
from Agents.manager_agent import Manager
from Agents.simulator_agent import SimulatorAgent
from Agents.team import TeamAgent
from Tools.data import TeamData
from Tools.enum import T1, T2
from Tools.game import Game
from Tools.utils import coin_toss

# Ajuste de constantes para el voleibol
CANT_RALLIES = 180  # Número máximo de rallies a simular
INTERVAL_MANAGER = 20  # Intervalo para decisiones del entrenador (sustituciones, tiempos muertos, etc.)


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
        statistics = self.game_statistics(
            self.game.instance - 1, self.game.cant_instances
        )
        yield field_str + "\n" + statistics

        while not self.game.is_finish():
            simulator.simulate_rally(set())
            field_str = str(self.game.field)
            statistics = self.game_statistics(
                self.game.instance - 1, self.game.cant_instances
            )
            yield field_str + "\n" + statistics

    def simulate_and_save(self):
        simulator = Simulator(self.t1, self.t2, self.game)
        simulator.start_match()

        while not self.game.is_finish():
            simulator.simulate_rally(set())

        return simulator.game.to_json()

    def game_statistics(self, instance: int, total_rallies: int) -> str:
        nh = f"\033[34m{self.t1.name}\033[0m"
        na = f"\033[31m{self.t2.name}\033[0m"
        sh = self.game.t1_sets
        sa = self.game.t2_sets
        ph = self.game.t1_score
        pa = self.game.t2_score
        current_set = self.game.current_set

        len_s = len(nh) + len(na) - 18
        return f"""
Set {current_set} - Rally {instance}/{total_rallies}
{nh}{' ' * (52 - len_s)}{na}
Sets Ganados: {sh}{' ' * 40}{sa}
Puntos en Set Actual: {ph}{' ' * 40}{pa}
"""


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
            self.game.field.move_ball(ball_position, (1, 1))
        else:
            self.game.serving_team = T2
            self.game.ball_possession_team = T2
            ball_position = self.game.field.find_ball()
            ball_position = (ball_position.row, ball_position.col)
            print("Sirve T2")
            self.game.field.move_ball(ball_position, (17, 1))

        self.game.start_rally()
        self.game.instance = 1

    def simulate_rally(
            self,
            mask: Set[Tuple[int, str]],
            heuristic_manager: bool = False,
            heuristic_player: bool = False,
    ):
        self.stack.append(len(self.dispatch.stack))

        # Iniciar el rally en el juego
        self.game.start_rally()

        # Simulation tick
        while not self.game.is_rally_over():
            current_team = self.game.ball_possession_team
            other_team = T1 if current_team == T2 else T2

            c_team: [TeamData] = self.game.t1 if current_team == T1 else self.game.t2
            o_team: [TeamData] = self.game.t2 if current_team == T1 else self.game.t1

            nothing_count = 0

            for player in c_team.on_field:
                player_action = self.get_next_player_actions(player, current_team)
                self.dispatch.dispatch(player_action)
                if player_action.__class__.__name__ == "Nothing" or player_action.__class__.__name__ == "Move":
                    nothing_count += 1
            if nothing_count == 6 and self.game.ball_possession_team == current_team:
                self.game.score_point(other_team)
                return

            print(str(self.game.field))
            nothing_count = 0
            for player in o_team.on_field:
                player_action = self.get_next_player_actions(player, other_team)
                self.dispatch.dispatch(player_action)
                if player_action.__class__.__name__ == "Nothing" or player_action.__class__.__name__ == "Move":
                    nothing_count += 1
            if nothing_count == 6 and self.game.ball_possession_team == other_team:
                self.game.score_point(current_team)
                return
            print(str(self.game.field))

        # Procesar el fin del rally
        self.game.handle_end_of_rally()

        # Incrementar el contador de instancias (rallies)
        self.game.instance += 1

        # Simular decisiones de los entrenadores
        self.simulate_managers(mask)

    def get_next_actions(self, team: str) -> [Action]:
        players = self.game.t1.on_field if team == T1 else self.game.t2.on_field
        actions: [Action] = []
        for player_number in players:
            sim = self.get_player_simulator(team, player_number, set())
            action = self.get_player_action(team, player_number, sim)
            actions.append(action)
        return actions

    def get_next_player_actions(self, player: int, team: str) -> [Action]:
        sim = self.get_player_simulator(team, player, set())
        return self.get_player_action(team, player, sim)

    def get_next_player(self, team: str) -> int:
        if team == T1:
            return self.team1.select_next_player()
        else:
            return self.team2.select_next_player()

    def get_player_action(self, team: str, player_number: int, sim: SimulatorAgent):
        # Obtener la acción que el jugador realizará
        if team == T1:
            return self.team1.players[player_number].play(sim)
        else:
            return self.team2.players[player_number].play(sim)

    def simulate_managers(self, mask: Set[Tuple[int, str]]):
        if self.game.instance % INTERVAL_MANAGER == 0:
            if (T1, "manager") not in mask:
                mask.add((T1, "manager"))
                sim = self.get_simulator(self.team1.manager, T1, mask)
                action = self.team1.manager.decide_action(sim)
                self.dispatch.dispatch(action)

            if (T2, "manager") not in mask:
                mask.add((T2, "manager"))
                sim = self.get_simulator(self.team2.manager, T2, mask)
                action = self.team2.manager.decide_action(sim)
                self.dispatch.dispatch(action)

    def get_simulator(self, manager: Manager, team: str, mask: Set[Tuple[int, str]]):
        if isinstance(manager.action_strategy, ActionSimulateStrategy):
            return SimulatorActionSimulateManager(self, team, mask)
        elif isinstance(manager.action_strategy, ActionMiniMaxStrategy):
            return SimulatorActionMiniMaxManager(self, team, mask)
        else:
            return SimulatorRandom(self.game)

    def get_player_simulator(self, team: str, player: int, mask: Set[Tuple[int, str]]):
        return SimulatorActionSimulatePlayer(self, team, player, mask)

    def reset_all(self):
        while self.game.instance != 1:
            self.reset_instance()

    def reset_instance(self):
        self.dispatch.reset()
        while len(self.dispatch.stack) != self.stack[-1]:
            self.dispatch.reset()
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
            self.simulator.simulate_rally(set())

    def reset(self):
        while self.simulator.game.instance != self.instance + 1:
            self.simulator.reset_instance()

    def simulate_current(self):
        self.simulator.simulate_rally(self.mask.copy())

    def reset_current(self):
        while len(self.simulator.dispatch.stack) != self.stack_len:
            self.simulator.dispatch.reset()

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
        self.simulator.simulate_rally({(self.player, self.team)})

    def reset(self):
        self.simulator.reset_instance()

    def simulate_current(self):
        self.simulator.simulate_rally(self.mask.copy())

    def reset_current(self):
        while len(self.simulator.dispatch.stack) != self.stack_len:
            self.simulator.dispatch.reset()

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
