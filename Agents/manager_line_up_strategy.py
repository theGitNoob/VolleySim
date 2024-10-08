from abc import ABC, abstractmethod
from random import choice
from typing import List

from Agents.simulator_agent import SimulatorAgent
from Tools.enum import T1, PlayerRole
from Tools.line_up import LineUp, StandardVolleyballLineUp
from Tools.player_data import PlayerData

CANT_SIMULATIONS = 1  # Número de simulaciones para evaluar las alineaciones


def players_by_role(players: List[PlayerData], role: PlayerRole) -> List[PlayerData]:
    """
    Filtra y ordena los jugadores que pueden desempeñar un rol específico.
    """
    eligible_players = [
        player
        for player in players
        if player.position == role.value or role.value in player.roles
    ]
    eligible_players.sort(key=lambda x: x.overall, reverse=True)
    return eligible_players


def possible_line_up(players: List[PlayerData], team_side: str) -> LineUp:
    """
    Genera una alineación posible asignando los mejores jugadores a cada rol.
    """
    roles = [
        PlayerRole.SETTER,
        PlayerRole.OUTSIDE_HITTER,
        PlayerRole.OUTSIDE_HITTER,
        PlayerRole.OPPOSITE_HITTER,
        PlayerRole.MIDDLE_BLOCKER,
        PlayerRole.LIBERO,
    ]
    lineup = StandardVolleyballLineUp(team_side=team_side)
    assigned_players = set()

    for role in roles:
        eligible_players = players_by_role(players, role)
        for player in eligible_players:
            if player.dorsal not in assigned_players:
                try:
                    lineup.add_player(player, role.value)
                    assigned_players.add(player.dorsal)
                    break
                except ValueError:
                    continue  # No hay posición disponible para este rol en la alineación actual

    # # Si faltan jugadores para completar la alineación, llenar con jugadores restantes
    # remaining_players = [p for p in players if p.dorsal not in assigned_players]
    # remaining_players.sort(key=lambda x: x.overall, reverse=True)
    #
    # while len([grid for grid in lineup.line_up.values() if grid.player is not None]) < 6 and remaining_players:
    #     player = remaining_players.pop(0)
    #     try:
    #         lineup.add_player(player, role.value)  # Asignar rol genérico
    #         assigned_players.add(player.dorsal)
    #     except ValueError:
    #         continue  # No hay posición disponible para este rol

    return lineup


def possible_line_ups(players: List[PlayerData], team_side: str) -> List[LineUp]:
    """
    Genera todas las combinaciones posibles de alineaciones basadas en los roles.
    """
    from itertools import permutations

    roles = [
        PlayerRole.SETTER,
        PlayerRole.OUTSIDE_HITTER,
        PlayerRole.OPPOSITE_HITTER,
        PlayerRole.MIDDLE_BLOCKER,
        PlayerRole.LIBERO,
    ]
    line_ups = []

    # Obtener los mejores jugadores para cada rol
    role_players = {role: players_by_role(players, role) for role in roles}

    # Generar permutaciones de roles
    role_permutations = list(permutations(roles))

    for perm in role_permutations:
        lineup = StandardVolleyballLineUp(team_side=team_side)
        assigned_players = set()
        valid_line_up = True

        for role in perm:
            eligible_players = role_players[role]
            for player in eligible_players:
                if player.dorsal not in assigned_players:
                    try:
                        lineup.add_player(player, role.value)
                        assigned_players.add(player.dorsal)
                        break
                    except ValueError:
                        continue  # No hay posición disponible para este rol en la alineación actual
            else:
                valid_line_up = False
                break  # No hay jugadores disponibles para este rol

        if (
            valid_line_up
            and len(
                [grid for grid in lineup.line_up.values() if grid.player is not None]
            )
            == 6
        ):
            line_ups.append(lineup)

    return line_ups if line_ups else [possible_line_up(players, team_side)]


class ManagerLineUpStrategy(ABC):
    @abstractmethod
    def get_line_up(self, team: str, simulator: SimulatorAgent) -> LineUp:
        pass


class LineUpRandomStrategy(ManagerLineUpStrategy):
    def get_line_up(self, team: str, simulator: SimulatorAgent) -> LineUp:
        """
        Selecciona una alineación al azar de entre las posibles alineaciones.
        """
        players = (
            list(simulator.game.t1.data.values())
            if team == T1
            else list(simulator.game.t2.data.values())
        )
        line_ups = possible_line_ups(players, team_side=team)
        return choice(line_ups)


class LineUpFixedStrategy(ManagerLineUpStrategy):
    def get_line_up(self, team: str, simulator: SimulatorAgent) -> LineUp:
        """
        Selecciona la mejor alineación posible basada en los jugadores disponibles.
        """
        players = (
            list(simulator.game.t1.data.values())
            if team == T1
            else list(simulator.game.t2.data.values())
        )
        line_ups = possible_line_ups(players, team_side=team)

        # Seleccionar la alineación con el mayor puntaje total
        best_line_up = max(
            line_ups,
            key=lambda lu: sum(
                player.overall
                for grid in lu.line_up.values()
                if grid.player is not None
                for player in [next(p for p in players if p.dorsal == grid.player)]
            ),
        )
        return best_line_up


class LineUpSimulateStrategy(ManagerLineUpStrategy):
    def get_line_up(self, team: str, simulator: SimulatorAgent) -> LineUp:
        """
        Simula varios partidos con diferentes alineaciones y elige la mejor.
        """
        print(
            f'El entrenador del equipo {"LOCAL" if team == T1 else "VISITANTE"} está seleccionando la alineación...'
        )

        # Obtener posibles alineaciones para ambos equipos
        t1_players = list(simulator.game.t1.data.values())
        t2_players = list(simulator.game.t2.data.values())

        t1_line_ups = possible_line_ups(t1_players, team_side="T1")
        t2_line_ups = possible_line_ups(t2_players, team_side="T2")

        results = []

        for i, t1_line_up in enumerate(t1_line_ups):
            for j, t2_line_up in enumerate(t2_line_ups):
                total_score = 0
                for _ in range(CANT_SIMULATIONS):
                    # Configurar el juego con las alineaciones actuales
                    simulator.game.reset()
                    simulator.game.conf_line_ups(t1_line_up, t2_line_up)
                    simulator.game.instance = 1

                    # Simular el partido o set
                    simulator.simulate()

                    # Obtener el resultado
                    t1_points = simulator.game.t1_score
                    t2_points = simulator.game.t2_score

                    # Acumular el puntaje (diferencia de puntos)
                    score_diff = (
                        t1_points - t2_points if team == T1 else t2_points - t1_points
                    )
                    total_score += score_diff

                    # Reiniciar el simulador y el juego
                    simulator.reset()
                    simulator.game.reset()

                # Almacenar los resultados
                results.append(
                    {
                        "line_up_index": i if team == T1 else j,
                        "total_score": total_score,
                    }
                )

        # Seleccionar la alineación con el mejor rendimiento
        best_result = max(results, key=lambda x: x["total_score"])
        best_line_up_index = best_result["line_up_index"]

        return (
            t1_line_ups[best_line_up_index]
            if team == T1
            else t2_line_ups[best_line_up_index]
        )
