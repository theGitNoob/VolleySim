# configuracion.py

from typing import Tuple

from pandas import DataFrame

from Agents.manager_action_strategy import (ActionMiniMaxStrategy,
                                            ActionRandomStrategy,
                                            ActionSimulateStrategy,
                                            ManagerActionStrategy)
from Agents.manager_line_up_strategy import (LineUpRandomStrategy,
                                             ManagerLineUpStrategy, LineUpFixedStrategy)
from Agents.player_strategy import (MinimaxStrategy, PlayerStrategy,
                                    RandomStrategy, VolleyballStrategy)
from Simulator.simulation_params import SimulationParams
from .gemini import query


def conf_game_llm(user_prompt: str, df: DataFrame) -> SimulationParams | None:
    try:
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


def teams_prompt(user_prompt: str, df: DataFrame) -> Tuple[str, str]:
    team_names = df["Team"].unique().tolist()
    team_names = [i for i in team_names if isinstance(i, str)]
    prompt = f"""
    Dada la siguiente lista de equipos: {team_names}
    y esta configuración del usuario: {user_prompt} 
    dime a que equipos hace referencia con el siguiente formato: `Nombre del equipo 1 vs Nombre del equipo 2`
    DEBES USAR EXACTAMENTE LOS NOMBRES QUE TE PROPORCIONÉ USANDO EL FORMATO DE 3 LETRAS SOLAMENTE
"""
    response = query(prompt + "\n" + "\n".join(team_names) + "\n" + user_prompt).strip()

    try:
        t1, t2 = [team.strip() for team in response.split(" vs ")]
        t1, t2 = t1.upper(), t2.upper()

        if t1 not in team_names or t2 not in team_names:
            raise Exception("Equipos no válidos")
        return t1, t2
    except Exception as e:
        print(f"Error al procesar los equipos: {response}, {e}")
        raise Exception("Error al obtener los equipos")


def managers_line_up_prompt(
        user_prompt: str,
) -> Tuple[ManagerLineUpStrategy, ManagerLineUpStrategy]:
    strategies = {
        "random": LineUpRandomStrategy(),
        "simulate": LineUpFixedStrategy(),
    }
    prompt = f"""
        Dada la siguiente lista de estrategias: {strategies.keys()}
        y esta configuración del usuario: {user_prompt} 
        dime a cual hace referencia con el siguiente formato: estrategia1 vs estrategia2
        DEBES USAR EXACTAMENTE LOS NOMBRES QUE TE PROPORCIONÉ
    """

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
    strategies = {
        "random": ActionRandomStrategy(),
        "simulate": ActionSimulateStrategy(),
        "minimax": ActionMiniMaxStrategy(),
    }
    prompt = f"""
        Dada la siguiente lista de estrategias para el entrenador: {strategies.keys()}
        y esta configuración del usuario: {user_prompt} 
        dime a cual hace referencia con el siguiente formato: estrategia1 vs estrategia2
        DEBES USAR EXACTAMENTE LOS NOMBRES QUE TE PROPORCIONÉ
    """

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
    strategies = {
        "random": RandomStrategy(),
        "heuristic": VolleyballStrategy(),
        "minimax": MinimaxStrategy(),
    }
    prompt = f"""
        Dada la siguiente lista de estrategias: {strategies.keys()}
        y esta configuración del usuario: {user_prompt} 
        dime a cual hace referencia con el siguiente formato: estrategia1 vs estrategia2
        DEBES USAR EXACTAMENTE LOS NOMBRES QUE TE PROPORCIONÉ
    """

    response = query(
        prompt + "\n" + "\n".join(strategies.keys()) + "\n" + user_prompt
    ).strip()

    try:
        t1, t2 = [strategy.strip() for strategy in response.split(" vs ")]

        return strategies[t1], strategies[t2]
    except Exception as e:
        print(f"Error al procesar las estrategias de jugadores: {response}, {e}")
        return VolleyballStrategy(), VolleyballStrategy()
