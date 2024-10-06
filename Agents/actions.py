# actions.py

from abc import ABC, abstractmethod
from random import random
from typing import List, Tuple

from Tools.data import PlayerData, StatisticsPlayer, StatisticsTeam
from Tools.enum import T1, T2
from Tools.game import Game


class Action(ABC):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__()
        self.player: int = player
        self.team: str = team
        self.game: Game = game

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
    def reset(self):
        pass


class Receive(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        # Reducir la resistencia del jugador

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
            opponent_team = T1 if self.team == T2 else T1
            self.game.score_point(opponent_team)

    def reset(self):
        # Revertir resistencia

        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.receives -= 1
        player_stats.receives -= 1

        if not self.success:
            # Revertir punto otorgado
            opponent_team = T1 if self.team == T2 else T1
            self.game.revert_point(opponent_team)


class Serve(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):

        # Actualizar estadísticas del equipo y del jugador
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves += 1
        player_stats.serves += 1

        # Determinar si el saque es exitoso
        serving_skill = self.get_player_data().p_serve
        #TODO test, change true
        self.success = True  #random() <= (serving_skill / 100)

        if not self.success:
            # Error en el saque, punto para el oponente
            opponent_team = T1 if self.team == T2 else T2
            self.game.score_point(opponent_team)

    def reset(self):
        # Revertir resistencia

        # Revertir estadísticas
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.serves -= 1
        player_stats.serves -= 1

        if not self.success:
            # Revertir el punto otorgado
            opponent_team = T1 if self.team == T2 else T2
            self.game.revert_point(opponent_team)


class Dig(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs += 1
        player_stats.digs += 1

        digging_skill = self.get_player_data().digging
        self.success = random() <= (digging_skill / 100)

        if not self.success:
            # Error en el dig, punto para el oponente
            opponent_team = T1 if self.team == T2 else T2
            self.game.score_point(opponent_team)

    def reset(self):

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.digs -= 1
        player_stats.digs -= 1

        if not self.success:
            # Revertir punto del oponente
            opponent_team = T1 if self.team == T2 else T2
            self.game.revert_point(opponent_team)


class Set(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.sets_won += 1
        #TODO configurar setting skill in player data segun la posicion
        setting_skill = 1679
        self.success = random() <= (setting_skill / 100)

    def reset(self):
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

        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.attacks += 1
        player_stats.attacks += 1

        attacking_skill = self.get_player_data().attacking
        self.success = random() <= (attacking_skill / 100)

        if self.success:
            # Intentar bloqueo del oponente
            opponent_team = T1 if self.team == T2 else T2
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
            opponent_team = T1 if self.team == T2 else T2
            self.game.score_point(opponent_team)

    def reset(self):

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
            opponent_team = T1 if self.team == T2 else T2
            self.game.revert_point(opponent_team)

    def select_blocker(self, team: str) -> int:
        # Lógica para seleccionar al jugador bloqueador
        team_data = self.game.t1 if team == T1 else self.game.t2
        # Seleccionar un bloqueador disponible
        return team_data.select_blocker()


class Block(Action):
    def __init__(self, player: int, team: str, game: Game) -> None:
        super().__init__(player, team, game)
        self.success: bool = False

    def execute(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks += 1
        player_stats.blocks += 1

        blocking_skill = self.get_player_data().blocking
        self.success = random() <= (blocking_skill / 100)

    def reset(self):
        team_stats = self.get_statistics()
        player_stats = self.get_player_statistics()

        team_stats.blocks -= 1
        player_stats.blocks -= 1


class Move(Action):
    def __init__(
            self,
            src: Tuple[int, int],
            dest: Tuple[int, int],
            player: int,
            team: str,
            game: Game,
    ) -> None:
        super().__init__(player, team, game)
        self.src = src
        self.dest = dest

    def execute(self):
        self.game.field.move_player(self.src, self.dest)

    def reset(self):
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

    def reset(self):
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
            opponent_team = T1 if action.team == T2 else T2
            self.game.score_point(opponent_team)
            self.game.change_serving_team()
        else:
            # Saque exitoso, el oponente intenta recibir
            opponent_team = T1 if action.team == T2 else T2
            self.game.move_ball((8, 4), (12, 4))
            receiver_player = self.game.get_closest_player_to_ball(opponent_team)
            receive_action = Receive(receiver_player, opponent_team, self.game)
            self.dispatch(receive_action)

    def receive_trigger(self, action: Receive):
        if not action.success:
            # Error en la recepción, punto para el oponente
            opponent_team = T1 if action.team == T2 else T2
            self.game.score_point(opponent_team)
            self.game.change_serving_team()
        else:
            # Recepción exitosa, proceder con la colocación
            setter_player = self.game.select_setter(action.team)
            set_action = Set(setter_player, action.team, self.game)
            self.dispatch(set_action)

    def set_trigger(self, action: Set):
        if not action.success:
            # Error en la colocación, punto para el oponente
            opponent_team = T1 if action.team == T2 else T2
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
            opponent_team = T1 if action.team == T2 else T2
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)
        else:
            # Ataque exitoso, el oponente intenta bloquear
            opponent_team = T1 if action.team == T2 else T2
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
            opponent_team = T1 if action.team == T2 else T2
            self.game.score_point(opponent_team)
            self.game.change_serving_team(opponent_team)

    def dig_trigger(self, action: Dig):
        if not action.success:
            # Error en la defensa, punto para el oponente
            opponent_team = T1 if action.team == T2 else T2
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
