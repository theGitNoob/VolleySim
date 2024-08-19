import csv
import random

columnas = [
    "Nombre",
    "Altura (cm)",
    "Resistencia",
    "Salto Máximo (cm)",
    "Velocidad (m/s)",
]


# Generar datos aleatorios
def generar_datos_aleatorios(num_registros):
    datos = []

    for i in range(num_registros):
        nombre = f"Jugador_{i+1}"
        altura = random.randint(150, 215)
        resistencia = round(random.uniform(1, 10), 2)
        salto_maximo = random.randint(20, 80)
        velocidad = round(random.uniform(2, 10), 2)
        datos.append([nombre, altura, resistencia, salto_maximo, velocidad])

    return datos


def exportar_a_csv(nombre_archivo, datos):
    with open(nombre_archivo, "w", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)
        escritor.writerows(datos)


datos_aleatorios = generar_datos_aleatorios(10)
exportar_a_csv("estadisticas.csv", datos_aleatorios)
