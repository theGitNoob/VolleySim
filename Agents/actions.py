import copy
from abc import ABC, abstractmethod
from random import random
from typing import List, Tuple

from Tools.data import PlayerData, PlayerStatistics, TeamStatistics
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

    def get_statistics(self) -> TeamStatistics:
        if self.team == T1:
            return self.game.t1.statistics
        else:
            return self.game.t2.statistics

    def get_player_statistics(self) -> PlayerStatistics:
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
        self.game_copy = copy.deepcopy(self.game)

        receiving_skill = self.get_player_data().p_receive
        self.success = random() <= receiving_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        self.game_copy = copy.deepcopy(self.game)
        serving_skill = self.get_player_data().p_serve

        self.success = random() <= serving_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        digging_skill = self.get_player_data().p_dig
        self.success = random() <= digging_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        setting_skill = self.get_player_data().p_set
        self.success = random() <= setting_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        attacking_skill = self.get_player_data().p_attack
        self.success = random() <= attacking_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        blocking_skill = self.get_player_data().p_block
        self.success = random() <= blocking_skill

    def rollback(self):
        recursive_update(self.game, self.game_copy)


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
        recursive_update(self.game, self.game_copy)


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


class Timeout(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__((0, 0), (0, 0), -1, team, game)

    def execute(self):
        # Registrar el tiempo muerto
        self.game.register_time_out(self.team)

    def rollback(self):
        # Revertir el tiempo muerto
        self.game.revert_timeout(self.team)


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
        # print(f"¡{self.team} celebra el punto! Pulsa Enter para continuar...")
        pass

    def rollback(self):
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
    def __init__(self, _: Game) -> None:
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

    @staticmethod
    def serve_trigger(action: Serve):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        team_stats = action.get_player_statistics()
        player_stats = action.get_player_statistics()
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            action.game.rally_over = True
            player_stats.total_serves += 1
            player_stats.errors += 1
            team_stats.errors += 1


        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1
            action.game.ball_possession_team = T1 if action.team == T2 else T2

            #
            player_stats.total_serves += 1
            player_stats.serves += 1
            team_stats.serves += 1

    @staticmethod
    def receive_trigger(action: Receive):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        team_stats = action.get_statistics()
        player_stats = action.get_player_statistics()

        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            action.game.rally_over = True
            # stats
            player.errors += 1
            player_stats.errors += 1
            team_stats.errors += 1
            player_stats.total_receives += 1

        else:
            ball_crossed_net = action.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                action.game.touches[action.team] = 0
            else:
                action.game.general_touches += 1
            action.game.has_ball_landed = False
            action.game.touches[action.team] += 1

            # stats 
            player_stats.total_receives += 1
            player_stats.receives += 1
            team_stats.receives += 1

    @staticmethod
    def set_trigger(action: Set):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team

        team_stats = action.get_statistics()
        player_stats = action.get_player_statistics()
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            # stats
            player.errors += 1
            player_stats.errors += 1
            team_stats.errors += 1

            action.game.rally_over = True

        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1

            # stats
            player_stats.total_sets += 1
            player_stats.sets += 1
            team_stats.sets += 1

    @staticmethod
    def attack_trigger(action: Attack):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        team_stats = action.get_statistics()
        player_stats = action.get_player_statistics()
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            action.game.rally_over = True

            # stats
            player.errors += 1
            player_stats.errors += 1
            team_stats.errors += 1
            player_stats.total_attacks += 1

        else:
            action.game.has_ball_landed = False
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1
            action.game.touches[action.team] += 1
            action.game.touches[action.team] = 0
            action.game.ball_possession_team = T1 if action.team == T2 else T2

            # stats
            player_stats.total_attacks += 1
            player_stats.attacks += 1
            team_stats.attacks += 1

    @staticmethod
    def block_trigger(action: Block):
        team_stats = action.get_statistics()
        player_stats = action.get_player_statistics()
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            player.errors += 1
            player_stats.errors += 1
            team_stats.errors += 1
            player_stats.total_blocks += 1

        else:
            action.game.has_ball_landed = False
            action.game.last_player_touched = action.player
            action.game.last_team_touched = action.team
            action.game.field.move_ball(action.src, action.dest)
            action.game.general_touches += 1

            # stats
            player_stats.total_blocks += 1
            player_stats.blocks += 1
            team_stats.blocks += 1

    @staticmethod
    def dig_trigger(action: Dig):
        action.game.last_player_touched = action.player
        action.game.last_team_touched = action.team
        action.game.general_touches += 1
        player_stats = action.get_player_statistics()
        team_stats = action.get_statistics()
        if not action.success:
            player = (
                action.game.t1.get_player(action.player)
                if action.team == T1
                else action.game.t2.get_player(action.player)
            )
            action.game.rally_over = True
            # stats
            player.errors += 1
            player_stats.errors += 1
            team_stats.errors += 1
            player_stats.total_digs += 1


        else:
            action.game.has_ball_landed = False
            ball_crossed_net = action.game.field.move_ball(action.src, action.dest)
            if ball_crossed_net:
                action.game.touches[action.team] = 0
                action.game.ball_possession_team = T1 if action.team == T2 else T2
            else:
                action.game.touches[action.team] += 1
            # stats
            player_stats.total_digs += 1
            player_stats.digs += 1
            team_stats.digs += 1

    def rollback(self):
        # Deshacer la última acción
        if len(self.lazy_stack) != 0 and self.lazy_stack[-1] == self.stack[-1]:
            self.lazy_stack.pop()
        if self.stack:
            action = self.stack.pop()
            action.rollback()
