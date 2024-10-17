import os
from time import time

import pandas as pd

from Simulator.build_data import conf_game
from starting_params import all_random

df = pd.read_csv("data/VNL2024Men.csv")
# df.loc[:, df.columns.str.startswith("p_")] = 50
df["Dorsal"] = range(1, len(df) + 1)

# params = conf_game_llm(input("""
# Describe tu simulación, específica:
# * equipo 1
# * equipo 2
# * estrategia del manager local para tomar decisiones
# * estrategia del manager visitante para tomar decisiones
# * estrategias de los jugadores para tomar decisiones
# 
# """
#     ),
#     df,
# )

params = all_random.simulation_params

if params is None:
    print("No se pudo inferir los parámetros de la simulación")
    exit()

sim = conf_game(params, df)


def clear_console():
    if os.name == "posix":
        os.system("clear")
    elif os.name in ["ce", "nt", "dos"]:
        os.system("cls")


# print(sim.simulate_and_save())
current_time = time()
for s in sim.simulate():
    # time.sleep(0.5)
    clear_console()
    print(s)
print(time() - current_time)
