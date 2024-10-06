from typing import Generator

from Agents.simulator_agent import SimulatorAgent
from Tools.field import *

from .actions import *
from .player_strategy import PlayerStrategy, VolleyballStrategy


class Player:
    def __init__(self, dorsal: int, team: str, strategy: PlayerStrategy) -> None:
        self.strategy = strategy
        self.heuristic_strategy = VolleyballStrategy()
        self.dorsal = dorsal
        self.team = team

    def possible_actions(self, game: Game) -> List[Action]:
        visible_grids, p_grid = self.get_perceptions(game)
        actions = self.construct_actions(game, visible_grids, p_grid)
        return actions

    def play(self, simulator: SimulatorAgent):
        action = self.strategy.select_action(self.possible_actions, simulator)
        return action

    def play_heuristic(self, simulator: SimulatorAgent):
        action = self.heuristic_strategy.select_action(self.possible_actions, simulator)
        return action

    def get_data(self, game: Game) -> PlayerData:
        if self.team == T1:
            return game.t1.data[self.dorsal]
        else:
            return game.t2.data[self.dorsal]

    def get_perceptions(self, game: Game) -> Tuple[List[GridField], GridField]:
        p_grid: GridField = game.field.find_player(self.dorsal, self.team)
        visible_grids: List[GridField] = game.field.neighbor_grids(p_grid, 100)
        return visible_grids, p_grid

    @staticmethod
    def empty_adjacent_grids(
        visible_grids: List[GridField], p_grid: GridField
    ) -> Generator[GridField, None, None]:
        for g in visible_grids:
            if p_grid.is_contiguous(g) and g.is_empty():
                yield g

    def friendly_grids(
        self, visible_grids: List[GridField]
    ) -> Generator[GridField, None, None]:
        for g in visible_grids:
            if g.team == self.team:
                yield g

    def construct_actions(
        self, game: Game, visible_grids: List[GridField], p_grid: GridField
    ) -> List[Action]:
        actions: List[Action] = [Nothing(self.dorsal, self.team, game)]

        # TODO: Remove
        # if self.get_data(game).stamina <= 0:
        #     return actions

        # Comprobar si es nuestro turno de servir y si el jugador es el servidor
        if game.is_our_serve(self.team) and game.is_player_server(self.dorsal):
            actions.append(Serve(self.dorsal, self.team, game))
        elif game.is_ball_on_our_side(self.team):
            # La pelota está en nuestro lado
            if game.is_ball_coming_to_player(self.dorsal, self.team):
                # El jugador puede hacer un dig
                actions.append(Dig(self.dorsal, self.team, game))
            else:
                # El jugador puede colocar o atacar si no se han hecho 3 toques
                if game.touches[self.team] < 3:
                    actions.append(Set(self.dorsal, self.team, game))
                    actions.append(Attack(self.dorsal, self.team, game))
                # El jugador puede moverse dentro de la cancha
                for grid in self.empty_adjacent_grids(visible_grids, p_grid):
                    dest = (grid.row, grid.col)
                    actions.append(
                        Move(
                            (p_grid.row, p_grid.col), dest, self.dorsal, self.team, game
                        )
                    )
        else:
            # La pelota está en el lado del oponente o viene un ataque
            if game.is_opponent_attacking():
                # El jugador puede bloquear
                actions.append(Block(self.dorsal, self.team, game))
                actions.append(Receive(self.dorsal, self.team, game))
            else:
                # El jugador puede reposicionarse
                for grid in self.empty_adjacent_grids(visible_grids, p_grid):
                    dest = (grid.row, grid.col)
                    actions.append(
                        Move(
                            (p_grid.row, p_grid.col), dest, self.dorsal, self.team, game
                        )
                    )

        return actions
