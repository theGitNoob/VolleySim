import os

import pandas as pd

from llm.conf_game_llm import conf_game_llm
from Simulator.build_data import conf_game

df = pd.read_csv("data/VNL2024Men.csv")
# df.loc[:, df.columns.str.startswith("p_")] = 50
df["Dorsal"] = range(1, len(df) + 1)

params = conf_game_llm(
    input(
        """
Describe tu simulación, especifica:
* equipo 1
* equipo 2
* estrategia del manager local para tomar decisiones
* estrategia del manager visitante para tomar decisiones
* estrategias de los jugadores para tomar decisiones

"""
    ),
    df,
)
# params = conf_game_llm("Quiero un partido entre cuba y argentina", df)

# Ejemplo de parámetros de simulación

# starting_params: SimulationParams = SimulationParams(
#     names=('T1', 'T2'),
#     managers_line_up=(None, None),
#     managers_action_strategy=(None, None),
#     players_action_strategy=(None, None)
# )
# params = minimax_vs_minimax_player

if params is None:
    print("No se pudo inferir los parámetros de la simulación")
    exit()

sim = conf_game(params, df)


def clear_console():
    if os.name == "posix":
        os.system("clear")
    elif os.name in ["ce", "nt", "dos"]:
        os.system("cls")


for s in sim.simulate():
    # time.sleep(0.5)
    clear_console()
    print(s)
