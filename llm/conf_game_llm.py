# configuracion.py

from typing import Tuple

from pandas import DataFrame

from Agents.manager_action_strategy import (ActionMiniMaxStrategy,
                                            ActionRandomStrategy,
                                            ActionSimulateStrategy,
                                            ManagerActionStrategy)
from Agents.manager_line_up_strategy import (LineUpRandomStrategy,
                                             LineUpSimulateStrategy,
                                             ManagerLineUpStrategy)
from Agents.player_strategy import PlayerStrategy, VolleyballStrategy
from Simulator.simulation_params import SimulationParams

from .gemini import query


def conf_game_llm(user_prompt: str, df: DataFrame) -> SimulationParams | None:
    try:
        # league = league_prompt(user_prompt, df)
        names = teams_prompt(user_prompt, df)
        managers_line_up = managers_line_up_prompt(user_prompt)
        managers_action = managers_action_prompt(user_prompt)
        players_action = players_action_prompt(user_prompt)
        return SimulationParams(
            names, managers_line_up, managers_action, players_action
        )
    except Exception as e:
        print(f"Error en la configuración del juego: {e}")
        return None


def league_prompt(user_prompt: str, df: DataFrame) -> str:
    league_names = df["Team"].unique()
    league_names = [i for i in league_names if isinstance(i, str)]

    prompt = """
Tengo la siguiente lista de ligas y esta consulta definida por el usuario. Del texto introducido por el usuario, dime 
de qué liga el usuario desea simular el juego de voleibol. El formato de ejemplo es: Liga Nacional de Voleibol
"""
    league = query(prompt + "\n" + "\n".join(league_names) + "\n" + user_prompt).strip()

    if league not in league_names:
        print(f"Liga no encontrada: {league}")
        raise Exception("Liga no válida")

    return league


def teams_prompt(user_prompt: str, df: DataFrame) -> Tuple[str, str]:
    team_names = df["Team"].unique().tolist()
    team_names = [i.lower() for i in team_names]
    prompt = """
Tengo la siguiente lista de equipos y esta consulta definida por el usuario. Del texto introducido por el usuario, dime 
qué equipo es el local y cuál es el visitante, con el siguiente formato: Equipo A vs Equipo B. El de la izquierda
es el equipo local y el de la derecha el equipo visitante.
"""
    response = query(
        prompt + "\n" + "\n".join(team_names[:20]) + "\n" + user_prompt
    ).strip()

    try:
        t1, t2 = [team.strip() for team in response.split(" vs ")]
        t1, t2 = t1.lower(), t2.lower()

        if t1 not in team_names or t2 not in team_names:
            raise Exception("Equipos no válidos")
        return t1, t2
    except Exception as e:
        print(f"Error al procesar los equipos: {response}, {e}")
        raise Exception("Error al obtener los equipos")


def managers_line_up_prompt(
    user_prompt: str,
) -> Tuple[ManagerLineUpStrategy, ManagerLineUpStrategy]:
    prompt = """
Tengo la siguiente lista de estrategias para escoger la alineación inicial para el manager de mi simulación de voleibol, 
y esta consulta definida por el usuario. Del texto introducido por el usuario, dime qué estrategia de alineación desea
el manager local y cuál desea el visitante, con el siguiente formato: random vs simulate. La de la izquierda
es la estrategia del manager local y la de la derecha es la estrategia del manager visitante.
"""

    strategies = {
        "random": LineUpRandomStrategy(),
        "simulate": LineUpSimulateStrategy(),
    }

    response = query(
        prompt + "\n" + "\n".join(strategies.keys()) + "\n" + user_prompt
    ).strip()

    try:
        t1, t2 = [strategy.strip() for strategy in response.split(" vs ")]

        return strategies[t1], strategies[t2]
    except Exception as e:
        print(f"Error al procesar las estrategias de alineación: {response}, {e}")
        return LineUpRandomStrategy(), LineUpRandomStrategy()


def managers_action_prompt(
    user_prompt: str,
) -> Tuple[ManagerActionStrategy, ManagerActionStrategy]:
    prompt = """
Tengo la siguiente lista de estrategias para escoger las acciones durante el partido para el manager de mi simulación de voleibol, 
y esta consulta definida por el usuario. Del texto introducido por el usuario, dime qué estrategia de acciones 
desea el manager local y cuál desea el visitante, con el siguiente formato: random vs simulate. La 
de la izquierda es la estrategia del manager local y la de la derecha es la estrategia del manager visitante.
"""

    strategies = {
        "random": ActionRandomStrategy(),
        "simulate": ActionSimulateStrategy(),
        "minimax": ActionMiniMaxStrategy(),
    }

    response = query(
        prompt + "\n" + "\n".join(strategies.keys()) + "\n" + user_prompt
    ).strip()

    try:
        t1, t2 = [strategy.strip() for strategy in response.split(" vs ")]

        return strategies[t1], strategies[t2]
    except Exception as e:
        print(f"Error al procesar las estrategias de acción: {response}, {e}")
        return ActionRandomStrategy(), ActionRandomStrategy()


def players_action_prompt(user_prompt: str) -> Tuple[PlayerStrategy, PlayerStrategy]:
    prompt = """
Tengo la siguiente lista de estrategias para escoger las acciones durante el partido para los jugadores de mi simulación de voleibol, 
y esta consulta definida por el usuario. Del texto introducido por el usuario, dime qué estrategia de acciones 
desea el equipo local y cuál desea el visitante, con el siguiente formato: random vs heuristic. La 
de la izquierda es la estrategia del equipo local y la de la derecha es la estrategia del equipo visitante.
"""

    strategies = {
        # 'random': RandomStrategy(),
        "heuristic": VolleyballStrategy(),
        # 'minimax': MinimaxStrategy()  # Puedes descomentar si tienes implementada esta estrategia
    }

    response = query(
        prompt + "\n" + "\n".join(strategies.keys()) + "\n" + user_prompt
    ).strip()

    try:
        t1, t2 = [strategy.strip() for strategy in response.split(" vs ")]

        return strategies[t1], strategies[t2]
    except Exception as e:
        print(f"Error al procesar las estrategias de jugadores: {response}, {e}")
        return VolleyballStrategy(), VolleyballStrategy()
