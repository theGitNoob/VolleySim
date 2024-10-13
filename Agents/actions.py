# actions.py
import copy
from abc import ABC, abstractmethod
from random import random
from typing import List, Tuple

from Tools.data import PlayerData, StatisticsPlayer, StatisticsTeam
from Tools.enum import T1, T2
from Tools.game import Game


class Action(ABC):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__()
        self.src: Tuple[int, int] = src
        self.dest: Tuple[int, int] = dest
        self.player: int = player
        self.team: str = team
        self.game: Game = game
        self.game_copy = None

    def get_player_data(self) -> PlayerData:
        if self.team == T1:
            return self.game.t1.data[self.player]
        else:
            return self.game.t2.data[self.player]

    def get_statistics(self) -> StatisticsTeam:
        if self.team == T1:
            return self.game.t1.statistics
        else:
            return self.game.t2.statistics

    def get_player_statistics(self) -> StatisticsPlayer:
        if self.team == T1:
            return self.game.t1.players_statistics[self.player]
        else:
            return self.game.t2.players_statistics[self.player]

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class Receive(Action):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        # Actualizar estadísticas del equipo y del jugador
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives += 1
        player_stats.receives += 1

        # Determinar si la recepción es exitosa
        receiving_skill = self.get_player_data().p_receive
        self.success = random() <= receiving_skill

    def rollback(self):
        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives -= 1
        player_stats.receives -= 1
        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Serve(Action):
    def __init__(
        self,
        src: tuple[int, int],
        dest: tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        # Actualizar estadísticas del equipo y del jugador
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves += 1
        player_stats.serves += 1

        serving_skill = self.get_player_data().p_serve

        # TODO: Improve formula having in account the possition where the player whants the ball
        self.success = random() <= serving_skill

    def rollback(self):
        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves -= 1
        player_stats.serves -= 1

        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Dig(Action):
    def __init__(
        self,
        src: tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs += 1
        player_stats.digs += 1

        digging_skill = self.get_player_data().p_dig
        self.success = random() <= digging_skill

    def rollback(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs -= 1
        player_stats.digs -= 1

        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Set(Action):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        self.get_player_statistics()

        team_stats.sets_won += 1

        setting_skill = self.get_player_data().p_set
        self.success = random() <= setting_skill

    def rollback(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.sets -= 1
        player_stats.sets -= 1

        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Attack(Action):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks += 1
        player_stats.attacks += 1

        attacking_skill = self.get_player_data().p_attack
        self.success = random() <= attacking_skill

    def rollback(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks -= 1
        player_stats.attacks -= 1

        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Block(Action):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.success: bool = False

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks += 1
        player_stats.blocks += 1

        blocking_skill = self.get_player_data().p_block
        self.success = random() <= blocking_skill

    def rollback(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks -= 1
        player_stats.blocks -= 1

        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None


class Move(Action):
    def __init__(
        self,
        src: Tuple[int, int],
        dest: Tuple[int, int],
        player: int,
        team: str,
        game: Game,
    ) -> None:
        super().__init__(src, dest, player, team, game)
        self.src = src
        self.dest = dest

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)
        self.game.field.move_player(self.src, self.dest)

    def rollback(self):
        self.game.__dict__.update(self.game_copy.__dict__)
        self.game_copy = None
        # self.game.field.move_player(self.dest, self.src)


class Nothing(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), player, team, game)

    def execute(self):
        pass

    def rollback(self):
        pass


# Definición de la acción Substitution
class Substitution(Action):
    def __init__(self, player_out: int, player_in: int, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), player_out, team, game)
        self.player_in = player_in
        self.player_out = player_out

    def execute(self):
        team_data = self.game.t1 if self.team == T1 else self.game.t2

        # Registrar la sustitución en el historial
        team_data.substitution_history.append(
            {"out": self.player_out, "in": self.player_in, "set": self.game.current_set}
        )

        # Actualizar el line-up
        team_data.line_up.substitute_player(self.player_out, self.player_in)

        # Actualizar las listas de jugadores en cancha y en banca
        team_data.on_field.remove(self.player_out)
        team_data.on_field.add(self.player_in)
        team_data.on_bench.remove(self.player_in)
        team_data.on_bench.add(self.player_out)

        # Actualizar el campo de juego
        self.game.field.update_player_on_field(
            self.player_out, self.player_in, self.team
        )

    def rollback(self):
        team_data = self.game.t1 if self.team == T1 else self.game.t2

        # Revertir la sustitución
        team_data.substitution_history.pop()

        # Actualizar el line-up
        team_data.line_up.substitute_player(self.player_in, self.player_out)

        # Actualizar las listas de jugadores en cancha y en banca
        team_data.on_field.remove(self.player_in)
        team_data.on_field.add(self.player_out)
        team_data.on_bench.remove(self.player_out)
        team_data.on_bench.add(self.player_in)

        # Actualizar el campo de juego
        self.game.field.update_player_on_field(
            self.player_in, self.player_out, self.team
        )


# Definición de la acción Timeout
class Timeout(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # Registrar el tiempo muerto
        self.game.register_timeout(self.team)

        # Implementar lógica adicional si es necesario (pausar el juego, etc.)

    def rollback(self):
        # Revertir el tiempo muerto
        self.game.revert_timeout(self.team)


# Definición de la acción ManagerNothing
class ManagerNothing(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # No hace nada
        pass

    def rollback(self):
        # No hay nada que revertir
        pass


class ManagerCelebrate(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # Celebrar el punto
        pass

    def rollback(self):
        # No hay nada que revertir
        pass


class Dispatch:
    def __init__(self, game: Game) -> None:
        self.stack: List[Action] = []
        self.game = game

    def dispatch(self, action: Action):
        self.stack.append(action)
        action.execute()

        action_dest = action.dest

        # Verificar si la acción desencadena otros eventos
        if isinstance(action, Serve):
            # print(
            #     f"{action.team} {action.player} sirve {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.serve_trigger(action)
        elif isinstance(action, Receive):
            # print(
            #     f"{action.team} {action.player} recibe {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.receive_trigger(action)
        elif isinstance(action, Set):
            # print(
            #     f"{action.team} {action.player} coloca {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.set_trigger(action)
        elif isinstance(action, Attack):
            # print(
            #     f"{action.team} {action.player} ataque {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.attack_trigger(action)
        elif isinstance(action, Block):
            # print(
            #     f"{action.team} {action.player} bloqueo {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.block_trigger(action)
        elif isinstance(action, Dig):
            # print(
            #     f"{action.team} {action.player} defiende {'satisfactorio hacia: ' + str(action_dest) if action.success else 'fallido'}"
            # )
            self.dig_trigger(action)
        elif isinstance(action, Move):
            # print(f"{action.team} {action.player} se mueve hacia: {action_dest}")
            self.move_trigger(action)
        elif isinstance(action, Nothing):
            pass
            # print(f"{action.team} {action.player} no hizo nada")

    def move_trigger(self, action: Move):
        pass

    def serve_trigger(self, action: Serve):
        self.game.last_player_touched = action.player
        self.game.last_team_touched = action.team
        if not action.success:
            self.game.rally_over = True
        else:
            self.game.has_ball_landed = False
            self.game.field.move_ball(action.src, action.dest)
            self.game.general_touches += 1
            self.game.touches[action.team] += 1
            self.game.ball_possession_team = T1 if action.team == T2 else T2

    def receive_trigger(self, action: Receive):
        self.game.last_player_touched = action.player
        self.game.last_team_touched = action.team
        if not action.success:
            self.game.rally_over = True
        else:
            ball_crossed_net = self.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                self.game.touches[action.team] = 0
            else:
                self.game.general_touches += 1
            self.game.has_ball_landed = False
            self.game.touches[action.team] += 1

    def set_trigger(self, action: Set):
        self.game.last_player_touched = action.player
        self.game.last_team_touched = action.team
        if not action.success:
            self.game.rally_over = True

        else:
            self.game.has_ball_landed = False
            self.game.field.move_ball(action.src, action.dest)
            self.game.general_touches += 1
            self.game.touches[action.team] += 1

    def attack_trigger(self, action: Attack):
        self.game.last_player_touched = action.player
        self.game.last_team_touched = action.team
        if not action.success:
            self.game.rally_over = True

        else:
            self.game.has_ball_landed = False
            self.game.field.move_ball(action.src, action.dest)
            self.game.general_touches += 1
            self.game.touches[action.team] += 1
            self.game.touches[action.team] = 0
            self.game.ball_possession_team = T1 if action.team == T2 else T2

    def block_trigger(self, action: Block):
        if not action.success:
            # Bloqueo fallido, la bola pasa
            return
        else:
            self.game.has_ball_landed = False
            self.game.last_player_touched = action.player
            self.game.last_team_touched = action.team
            self.game.field.move_ball(action.src, action.dest)
            self.game.general_touches += 1

    def dig_trigger(self, action: Dig):
        self.game.last_player_touched = action.player
        self.game.last_team_touched = action.team
        self.game.general_touches += 1
        if not action.success:
            self.game.rally_over = True
        else:
            self.game.has_ball_landed = False
            ball_crossed_net = self.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                self.game.touches[action.team] = 0
                self.game.ball_possession_team = T1 if action.team == T2 else T2
            else:
                self.game.touches[action.team] += 1

    def rollback(self):
        # Deshacer la última acción
        if self.stack:
            action = self.stack.pop()
            action.rollback()
