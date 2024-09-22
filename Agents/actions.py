# actions.py

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from random import random, randint

from ..Tools.game import Game
from ..Tools.data import StatisticsTeam, StatisticsPlayer, PlayerData
from ..Tools.line_up import LineUp
from ..Tools.enum import HOME, AWAY


class Action(ABC):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__()
        self.player: int = player
        self.team: str = team
        self.game: Game = game

    def get_player_data(self) -> PlayerData:
        if self.team == HOME:
            return self.game.home.data[self.player]
        else:
            return self.game.away.data[self.player]

    def get_statistics(self) -> StatisticsTeam:
        if self.team == HOME:
            return self.game.home.statistics
        else:
            return self.game.away.statistics

    def get_player_statistics(self) -> StatisticsPlayer:
        if self.team == HOME:
            return self.game.home.players_statistics[self.player]
        else:
            return self.game.away.players_statistics[self.player]

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class Receive(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        # Reducir la resistencia del jugador
        self.get_player_data().stamina -= 1

        # Actualizar estadísticas del equipo y del jugador
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives += 1
        player_stats.receives += 1

        # Determinar si la recepción es exitosa
        receiving_skill = self.get_player_data().receiving
        self.success = random() <= (receiving_skill / 100)

        if not self.success:
            # Error en la recepción, punto para el oponente
            opponent_team = HOME if self.team == AWAY else HOME
            self.game.score_point(opponent_team)

    def reset(self):
        # Revertir resistencia
        self.get_player_data().stamina += 1

        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives -= 1
        player_stats.receives -= 1

        if not self.success:
            # Revertir punto otorgado
            opponent_team = HOME if self.team == AWAY else HOME
            self.game.revert_point(opponent_team)


class Serve(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        # Reducir la resistencia del jugador
        self.get_player_data().stamina -= 1

        # Actualizar estadísticas del equipo y del jugador
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves += 1
        player_stats.serves += 1

        # Determinar si el saque es exitoso
        serving_skill = self.get_player_data().serving
        self.success = random() <= (serving_skill / 100)

        if not self.success:
            # Error en el saque, punto para el oponente
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.score_point(opponent_team)

    def reset(self):
        # Revertir resistencia
        self.get_player_data().stamina += 1

        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves -= 1
        player_stats.serves -= 1

        if not self.success:
            # Revertir el punto otorgado
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.revert_point(opponent_team)


class Dig(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        self.get_player_data().stamina -= 1

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs += 1
        player_stats.digs += 1

        digging_skill = self.get_player_data().digging
        self.success = random() <= (digging_skill / 100)

        if not self.success:
            # Error en el dig, punto para el oponente
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.score_point(opponent_team)

    def reset(self):
        self.get_player_data().stamina += 1

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs -= 1
        player_stats.digs -= 1

        if not self.success:
            # Revertir punto del oponente
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.revert_point(opponent_team)


class Set(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        self.get_player_data().stamina -= 1

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.sets += 1
        player_stats.sets += 1

        setting_skill = self.get_player_data().setting
        self.success = random() <= (setting_skill / 100)

    def reset(self):
        self.get_player_data().stamina += 1

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.sets -= 1
        player_stats.sets -= 1


class Attack(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False
        self.blocked: bool = False
        self.block_action: Block = None

    def execute(self):
        self.get_player_data().stamina -= 2

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks += 1
        player_stats.attacks += 1

        attacking_skill = self.get_player_data().attacking
        self.success = random() <= (attacking_skill / 100)

        if self.success:
            # Intentar bloqueo del oponente
            opponent_team = HOME if self.team == AWAY else AWAY
            blocker_player = self.select_blocker(opponent_team)
            self.block_action = Block(blocker_player, opponent_team, self.game)
            self.block_action.execute()

            if self.block_action.success:
                self.blocked = True
                # Punto para el equipo oponente
                self.game.score_point(opponent_team)
            else:
                # Punto para el equipo atacante
                self.game.score_point(self.team)
        else:
            # Error en el ataque, punto para el oponente
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.score_point(opponent_team)

    def reset(self):
        self.get_player_data().stamina += 2

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks -= 1
        player_stats.attacks -= 1

        if self.success and self.block_action:
            self.block_action.reset()

        # Revertir el punto otorgado
        if self.success and not self.blocked:
            self.game.revert_point(self.team)
        else:
            opponent_team = HOME if self.team == AWAY else AWAY
            self.game.revert_point(opponent_team)

    def select_blocker(self, team: str) -> int:
        # Lógica para seleccionar al jugador bloqueador
        team_data = self.game.home if team == HOME else self.game.away
        # Seleccionar un bloqueador disponible
        return team_data.select_blocker()


class Block(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        self.get_player_data().stamina -= 2

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks += 1
        player_stats.blocks += 1

        blocking_skill = self.get_player_data().blocking
        self.success = random() <= (blocking_skill / 100)

    def reset(self):
        self.get_player_data().stamina += 2

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks -= 1
        player_stats.blocks -= 1


class Move(Action):
    def __init__(self, src: Tuple[int, int], dest: Tuple[int, int], player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.src = src
        self.dest = dest

    def execute(self):
        self.get_player_data().stamina -= 1
        self.game.field.move_player(self.src, self.dest)

    def reset(self):
        self.get_player_data().stamina += 1
        self.game.field.move_player(self.dest, self.src)


class Nothing(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)

    def execute(self):
        pass

    def reset(self):
        pass


# Definición de la acción Substitution
class Substitution(Action):
    def __init__(self, player_out: int, player_in: int, team: str, game: Game) -> None:
        super().__init__(player_out, team, game)
        self.player_in = player_in
        self.player_out = player_out

    def execute(self):
        team_data = self.game.home if self.team == HOME else self.game.away

        # Registrar la sustitución en el historial
        team_data.substitution_history.append({
            'out': self.player_out,
            'in': self.player_in,
            'set': self.game.current_set
        })

        # Actualizar el line-up
        team_data.line_up.substitute_player(self.player_out, self.player_in)

        # Actualizar las listas de jugadores en cancha y en banca
        team_data.on_field.remove(self.player_out)
        team_data.on_field.add(self.player_in)
        team_data.on_bench.remove(self.player_in)
        team_data.on_bench.add(self.player_out)

        # Actualizar el campo de juego
        self.game.field.update_player_on_field(self.player_out, self.player_in, self.team)

    def reset(self):
        team_data = self.game.home if self.team == HOME else self.game.away

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
        self.game.field.update_player_on_field(self.player_in, self.player_out, self.team)


# Definición de la acción Timeout
class Timeout(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__(-1, team, game)

    def execute(self):
        # Registrar el tiempo muerto
        self.game.register_timeout(self.team)

        # Implementar lógica adicional si es necesario (pausar el juego, etc.)

    def reset(self):
        # Revertir el tiempo muerto
        self.game.revert_timeout(self.team)


# Definición de la acción ManagerNothing
class ManagerNothing(Action):
    def __init__(self, team: str, game: Game) -> None:
        super().__init__(-1, team, game)

    def execute(self):
        # No hace nada
        pass

    def reset(self):
        # No hay nada que revertir
        pass


class Dispatch:
    def __init__(self, game: Game) -> None:
        self.stack: List[Action] = []
        self.game = game

    def dispatch(self, action: Action):
        self.stack.append(action)
        action.execute()

        # Verificar si la acción desencadena otros eventos
        if isinstance(action, Serve):
            self.serve_trigger(action)
        elif isinstance(action, Receive):
            self.receive_trigger(action)
        elif isinstance(action, Set):
            self.set_trigger(action)
        elif isinstance(action, Attack):
            self.attack_trigger(action)
        elif isinstance(action, Block):
            self.block_trigger(action)
        elif isinstance(action, Dig):
            self.dig_trigger(action)
        elif isinstance(action, Nothing):
            # No hace nada, podría implementar lógica adicional si es necesario
            pass

    def serve_trigger(self, action: Serve):
        if not action.success:
            # Error en el saque, punto para el oponente
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Saque exitoso, el oponente intenta recibir
            opponent_team = HOME if action.team == AWAY else AWAY
            receiver_player = self.game.select_receiver(opponent_team)
            receive_action = Receive(receiver_player, opponent_team, self.game)
            self.dispatch(receive_action)

    def receive_trigger(self, action: Receive):
        if not action.success:
            # Error en la recepción, punto para el oponente
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Recepción exitosa, proceder con la colocación
            setter_player = self.game.select_setter(action.team)
            set_action = Set(setter_player, action.team, self.game)
            self.dispatch(set_action)

    def set_trigger(self, action: Set):
        if not action.success:
            # Error en la colocación, punto para el oponente
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Colocación exitosa, proceder con el ataque
            attacker_player = self.game.select_attacker(action.team)
            attack_action = Attack(attacker_player, action.team, self.game)
            self.dispatch(attack_action)

    def attack_trigger(self, action: Attack):
        if not action.success:
            # Error en el ataque, punto para el oponente
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Ataque exitoso, el oponente intenta bloquear
            opponent_team = HOME if action.team == AWAY else AWAY
            blocker_player = self.game.select_blocker(opponent_team)
            block_action = Block(blocker_player, opponent_team, self.game)
            self.dispatch(block_action)

    def block_trigger(self, action: Block):
        if action.success:
            # Bloqueo exitoso, punto para el equipo bloqueador
            self.game.score_point(action.team)
            self.game.change_serving_team(action.team)
        else:
            # Bloqueo fallido, el equipo atacante gana el punto
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)

    def dig_trigger(self, action: Dig):
        if not action.success:
            # Error en la defensa, punto para el oponente
            opponent_team = HOME if action.team == AWAY else AWAY
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Defensa exitosa, proceder con la colocación
            setter_player = self.game.select_setter(action.team)
            set_action = Set(setter_player, action.team, self.game)
            self.dispatch(set_action)

    def reset(self):
        # Deshacer la última acción
        if self.stack:
            action = self.stack.pop()
            action.reset()
