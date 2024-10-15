# actions.py
import copy
from abc import ABC, abstractmethod
from random import random
from typing import List, Tuple

from Tools.data import PlayerData, StatisticsPlayer, StatisticsTeam
from Tools.enum import T1, T2
from Tools.game import Game


def recursive_update(original, backup):
    for key, value in backup.__dict__.items():
        if isinstance(value, (int, float, str, bool, tuple)):
            setattr(original, key, value)
        elif isinstance(value, list):
            setattr(
                original,
                key,
                [
                    recursive_update(orig, back) if hasattr(orig, "__dict__") else back
                    for orig, back in zip(getattr(original, key), value)
                ],
            )
        elif hasattr(value, "__dict__"):
            recursive_update(getattr(original, key), value)
        else:
            setattr(original, key, copy.deepcopy(value))


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives -= 1
        player_stats.receives -= 1
        if self.success:
            self.game.field.move_ball(self.dest, self.src)
        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves -= 1
        player_stats.serves -= 1
        if self.success:
            self.game.field.move_ball(self.dest, self.src)

        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs -= 1
        player_stats.digs -= 1
        if self.success:
            self.game.field.move_ball(self.dest, self.src)

        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.sets -= 1
        player_stats.sets -= 1
        if self.success:
            self.game.field.move_ball(self.dest, self.src)

        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks -= 1
        player_stats.attacks -= 1
        if self.success:
            self.game.field.move_ball(self.dest, self.src)

        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        recursive_update(self.game, self.game_copy)
        return
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks -= 1
        player_stats.blocks -= 1

        if self.success:
            self.game.field.move_ball(self.dest, self.src)

        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None


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
        # self.game.__dict__.update(self.game_copy.__dict__)
        # self.game_copy = None
        recursive_update(self.game, self.game_copy)
        return
        # self.game.field.move_player(self.dest, self.src)

        # self.game.field.move_player(self.dest, self.src)


class Nothing(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), player, team, game)

    def execute(self):
        pass

    def rollback(self):
        pass


class LazyAction(Action, ABC):
    @abstractmethod
    def lazy_execute(self):
        pass

    @abstractmethod
    def lazy_reset(self):
        pass


# Definición de la acción Substitution
class Substitution(LazyAction):
    def lazy_execute(self):
        # Actualizar el line-up
        team_data = self.game.t1 if self.team == T1 else self.game.t2
        team_data.line_up.substitute_player(self.player_out, self.player_in)

        if self.player in team_data.unavailable:
            team_data.substitution_history.remove((self.player_out, self.player_in))
            self.not_execute = True
            return
            # Actualizar las listas de jugadores en cancha y en banca
        team_data.on_field.remove(self.player_out)
        team_data.on_field.add(self.player_in)
        team_data.on_bench.remove(self.player_in)
        team_data.on_bench.add(self.player_out)
        team_data.unavailable.add(self.player_out)

        # Actualizar el campo de juego
        self.game.field.update_player_on_field(self.player_in, self.player_out)

    def lazy_reset(self):
        # Actualizar el line-up
        team_data = self.game.t1 if self.team == T1 else self.game.t2

        if self.not_execute:
            self.not_execute = False
            team_data.substitution_history.append((self.player_out, self.player_in))
            return

        team_data.line_up.substitute_player(self.player_in, self.player_out)

        # Actualizar las listas de jugadores en cancha y en banca
        team_data.on_field.remove(self.player_in)
        team_data.on_field.add(self.player_out)
        team_data.on_bench.remove(self.player_out)
        team_data.on_bench.add(self.player_in)

        # Actualizar el campo de juego
        self.game.field.update_player_on_field(self.player_out, self.player_in)

    def __init__(self, player_out: int, player_in: int, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), player_out, team, game)
        self.player_in = player_in
        self.player_out = player_out
        self.not_execute: bool = False

    def execute(self):
        self.game_copy = copy.deepcopy(self.game)

        team_data = self.game.t1 if self.team == T1 else self.game.t2
        team_data.substitution_history.append((self.player_out, self.player_in))

    def rollback(self):
        team_data = self.game.t1 if self.team == T1 else self.game.t2

        team_data.substitution_history.remove((self.player_out, self.player_in))


# Definición de la acción Timeout
class Timeout(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # Registrar el tiempo muerto
        self.game.register_time_out(self.team)
        # print("Tiempo muerto de " + self.team + ". Pulsa Enter para continuar...")
        # input()

    def rollback(self):
        # Revertir el tiempo muerto
        self.game.revert_timeout(self.team)


# Definición de la acción ManagerNothing
class ManagerNothing(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # print(f"{self.team} decide no hacer nada")
        pass

    def rollback(self):
        # No hay nada que revertir
        pass


class ManagerCelebrate(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        print(f"¡{self.team} celebra el punto! Pulsa Enter para continuar...")
        # input()

    def rollback(self):
        # No hay nada que revertir
        pass


class CompressAction(Action):
    def __init__(self, actions: List[LazyAction]) -> None:
        super().__init__((0, 0), (0, 0), -1, "", None)
        self.actions: List[LazyAction] = actions

    def execute(self):
        for action in self.actions:
            action.lazy_execute()

    def rollback(self):
        self.actions.reverse()
        for action in self.actions:
            action.lazy_reset()


class RestoreLineupAction(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), player, team, game)

    def execute(self):
        pass

    def rollback(self):
        pass


class Dispatch:
    def __init__(self, game: Game) -> None:
        self.stack: List[Action] = []
        self.lazy_stack: List[Action | LazyAction] = []
        # self.game = game

    def clear_lazy(self):
        action = CompressAction(self.lazy_stack.copy())
        self.dispatch(action)
        self.lazy_stack.clear()

    def dispatch(self, action: Action):
        if isinstance(action, LazyAction):
            self.lazy_stack.append(action)
        if isinstance(action, RestoreLineupAction):
            self.clear_lazy()

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

        elif isinstance(action, Substitution):
            # print(
            #     f"{action.team} {action.player_out} sale y {action.player_in} entra al campo"
            # )
            pass

        elif isinstance(action, Timeout):
            # print(f"{action.team} pide tiempo muerto")
            pass

        elif isinstance(action, ManagerNothing):
            # print(f"{action.team} no hizo nada")
            pass

    def move_trigger(self, action: Move):
        pass

    def serve_trigger(self, action: Serve):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True
        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1
            action.game.ball_possession_team = T1 if action.team == T2 else T2

    def receive_trigger(self, action: Receive):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True
        else:
            ball_crossed_net = action.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                action.game.touches[action.team] = 0
            else:
                action.game.general_touches += 1
            action.game.has_ball_landed = False
            action.game.touches[action.team] += 1

    def set_trigger(self, action: Set):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True

        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1

    def attack_trigger(self, action: Attack):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True

        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1
            action.game.touches[action.team] = 0
            action.game.ball_possession_team = T1 if action.team == T2 else T2

    def block_trigger(self, action: Block):
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            return
        else:
            action.game.has_ball_landed = False
            action.game.last_player_touched = action.player
            action.game.last_team_touched = action.team
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1

    def dig_trigger(self, action: Dig):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        action.game.general_touches += 1
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True
        else:
            action.game.has_ball_landed = False
            ball_crossed_net = action.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                action.game.touches[action.team] = 0
                action.game.ball_possession_team = T1 if action.team == T2 else T2
            else:
                action.game.touches[action.team] += 1

    def rollback(self):
        # Deshacer la última acción
        if len(self.lazy_stack) != 0 and self.lazy_stack[-1] == self.stack[-1]:
            self.lazy_stack.pop()
        if self.stack:
            action = self.stack.pop()
            action.rollback()
