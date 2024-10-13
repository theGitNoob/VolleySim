import os
import time

import pandas as pd

from Simulator.build_data import conf_game
from starting_params import minimax_vs_minimax_player

df = pd.read_csv("data/VNL2024Men.csv")
# df.loc[:, df.columns.str.startswith("p_")] = 50
df["Dorsal"] = range(1, len(df) + 1)

# params = conf_game_llm(input(
#     """
# Describe tu simulación, especifica:
# * liga
# * equipo 1
# * equipo 2
# * estrategia del manager local para elegir la alineación
# * estrategia del manager visitante para elegir la alineación
# * estrategias de los jugadores para tomar decisiones
#
# """), df)
# params = conf_game_llm(
#     "Quiero un partido entre cuba y argentina",
#     df
# )

# Ejemplo de parámetros de simulación

# starting_params: SimulationParams = SimulationParams(
#     names=('T1', 'T2'),
#     managers_line_up=(None, None),
#     managers_action_strategy=(None, None),
#     players_action_strategy=(None, None)
# )
params = minimax_vs_minimax_player

if params is None:
    print("No se pudo inferir los parámetros de la simulación")
    exit()

# print('Simulación configurada correctamente')

sim = conf_game(params.simulation_params, df)


def clear_console():
    if os.name == "posix":
        os.system("clear")
    elif os.name in ["ce", "nt", "dos"]:
        os.system("cls")


for s in sim.simulate():
    # time.sleep(0.5)
    clear_console()
    print(s)
