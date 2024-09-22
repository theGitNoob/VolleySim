# simulator.py

from typing import Generator, Set, Tuple, List
from ..Agents.actions import Dispatch
from ..Agents.team import TeamAgent
from ..Tools.game import Game
from ..Tools.data import TeamData
from ..Agents.simulator_agent import SimulatorAgent
from ..Agents.manager_agent import Manager
from ..Agents.manager_action_strategy import ActionSimulateStrategy, ActionMiniMaxStrategy
from ..Tools.enum import HOME, AWAY

# Ajuste de constantes para el voleibol
CANT_RALLIES = 180  # Número máximo de rallies a simular
INTERVAL_MANAGER = 20  # Intervalo para decisiones del entrenador (sustituciones, tiempos muertos, etc.)


class VolleyballSimulation:
    def __init__(self, home: Tuple[TeamAgent, TeamData], away: Tuple[TeamAgent, TeamData]) -> None:
        self.home: TeamAgent = home[0]
        self.away: TeamAgent = away[0]
        self.game: Game = Game(home[1], away[1], CANT_RALLIES)

    def simulate(self) -> Generator[str, None, None]:
        simulator = Simulator(self.home, self.away, self.game)
        simulator.start_match()

        field_str = str(self.game.field)
        statistics = self.game_statistics(self.game.instance - 1, self.game.cant_instances)
        yield field_str + '\n' + statistics

        while not self.game.is_finish():
            simulator.simulate_rally(set())
            field_str = str(self.game.field)
            statistics = self.game_statistics(self.game.instance - 1, self.game.cant_instances)
            yield field_str + '\n' + statistics

    def simulate_and_save(self):
        simulator = Simulator(self.home, self.away, self.game)
        simulator.start_match()

        while not self.game.is_finish():
            simulator.simulate_rally(set())

        return simulator.game.to_json()

    def game_statistics(self, instance: int, total_rallies: int) -> str:
        nh = f'\033[34m{self.home.name}\033[0m'
        na = f'\033[31m{self.away.name}\033[0m'
        sh = self.game.home_sets
        sa = self.game.away_sets
        ph = self.game.home_score
        pa = self.game.away_score
        current_set = self.game.current_set

        len_s = len(nh) + len(na) - 18
        return f"""
Set {current_set} - Rally {instance}/{total_rallies}
{nh}{' ' * (52 - len_s)}{na}
Sets Ganados: {sh}{' ' * 40}{sa}
Puntos en Set Actual: {ph}{' ' * 40}{pa}
"""


class Simulator:
    def __init__(self, home: TeamAgent, away: TeamAgent, game: Game) -> None:
        self.home: TeamAgent = home
        self.away: TeamAgent = away
        self.game: Game = game
        self.stack: List[int] = []
        self.dispatch = Dispatch(self.game)  # Ahora Dispatch recibe la instancia de Game

    def start_match(self):
        self.game.instance = 0
        home_lineup = self.home.manager.get_line_up(SimulatorLineUpManager(self))
        away_lineup = self.away.manager.get_line_up(SimulatorLineUpManager(self))
        self.game.conf_line_ups(home_lineup, away_lineup)

        # Determinar equipo que sirve primero
        self.game.serving_team = HOME  # O puedes elegir aleatoriamente
        self.game.start_rally()
        self.game.instance = 1

    def simulate_rally(self, mask: Set[Tuple[int, str]]):
        self.stack.append(len(self.dispatch.stack))

        # Iniciar el rally en el juego
        self.game.start_rally()

        while not self.game.is_rally_over():
            current_team = self.game.ball_possession_team

            # Obtener acción del jugador
            action = self.get_next_action(current_team)
            self.dispatch.dispatch(action)
            # La acción y el dispatch actualizan el estado del juego

        # Procesar el fin del rally
        self.game.handle_end_of_rally()

        # Incrementar el contador de instancias (rallies)
        self.game.instance += 1

        # Simular decisiones de los entrenadores
        self.simulate_managers(mask)

    def get_next_action(self, team: str):
        # Determinar el siguiente jugador que actuará
        player_number = self.get_next_player(team)
        sim = self.get_player_simulator(team, player_number, set())
        action = self.get_player_action(team, player_number, sim)
        return action

    def get_next_player(self, team: str) -> int:
        # Lógica para seleccionar el siguiente jugador que realizará una acción
        # Puede basarse en la posición, función, o estrategia del equipo
        if team == HOME:
            return self.home.select_next_player()
        else:
            return self.away.select_next_player()

    def get_player_action(self, team: str, player_number: int, sim: SimulatorAgent):
        # Obtener la acción que el jugador realizará
        if team == HOME:
            return self.home.players[player_number].play(sim)
        else:
            return self.away.players[player_number].play(sim)

    def simulate_managers(self, mask: Set[Tuple[int, str]]):
        if self.game.instance % INTERVAL_MANAGER == 0:
            if not (HOME, 'manager') in mask:
                mask.add((HOME, 'manager'))
                sim = self.get_simulator(self.home.manager, HOME, mask)
                action = self.home.manager.decide_action(sim)
                self.dispatch.dispatch(action)

            if not (AWAY, 'manager') in mask:
                mask.add((AWAY, 'manager'))
                sim = self.get_simulator(self.away.manager, AWAY, mask)
                action = self.away.manager.decide_action(sim)
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
    def __init__(self, simulator: Simulator, team: str, player: int, mask: Set[Tuple[int, str]]):
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
            self.simulator.simulate_rally({(HOME, 'manager'), (AWAY, 'manager')})

    def reset(self):
        for _ in range(INTERVAL_MANAGER):
            self.simulator.reset_instance()

    def simulate_current(self):
        mask = self.mask.copy()
        if self.team == HOME:
            mask.add((AWAY, 'manager'))
        else:
            mask.add((HOME, 'manager'))
        self.simulator.simulate_rally(mask)
