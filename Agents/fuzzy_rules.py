import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def fuzzy_defensive_position():
    # Definir los universos de discurso para las variables de entrada y salida
    distance_to_position = ctrl.Antecedent(np.arange(0, 18.1, 0.1), 'distance_to_position')  # Distancia en metros
    distance_to_ball = ctrl.Antecedent(np.arange(0, 18.1, 0.1), 'distance_to_ball')
    player_role = ctrl.Antecedent(np.arange(0, 5, 1), 'player_role')
    defensive_position = ctrl.Consequent(np.arange(0, 101, 1), 'defensive_position')

    # Definir las funciones de membresía para distance_to_position
    distance_to_position['close'] = fuzz.trimf(distance_to_position.universe, [0, 0, 6])
    distance_to_position['medium'] = fuzz.trimf(distance_to_position.universe, [4, 9, 14])
    distance_to_position['far'] = fuzz.trimf(distance_to_position.universe, [12, 18, 18])

    # Definir las funciones de membresía para distance_to_ball
    distance_to_ball['close'] = fuzz.trimf(distance_to_ball.universe, [0, 0, 6])
    distance_to_ball['medium'] = fuzz.trimf(distance_to_ball.universe, [4, 9, 14])
    distance_to_ball['far'] = fuzz.trimf(distance_to_ball.universe, [12, 18, 18])

    # Definir las funciones de membresía para player_role
    player_role['setter'] = fuzz.trimf(player_role.universe, [0, 0, 0])
    player_role['middle_blocker'] = fuzz.trimf(player_role.universe, [1, 1, 1])
    player_role['outside_hitter'] = fuzz.trimf(player_role.universe, [2, 2, 2])
    player_role['opposite'] = fuzz.trimf(player_role.universe, [3, 3, 3])
    player_role['libero'] = fuzz.trimf(player_role.universe, [4, 4, 4])

    # Definir las funciones de membresía para defensive_position
    defensive_position['bad'] = fuzz.trimf(defensive_position.universe, [0, 0, 50])
    defensive_position['normal'] = fuzz.trimf(defensive_position.universe, [25, 50, 75])
    defensive_position['good'] = fuzz.trimf(defensive_position.universe, [50, 100, 100])

    # Definir las reglas
    rule1 = ctrl.Rule(distance_to_ball['close'] & player_role['libero'], defensive_position['good'])
    rule2 = ctrl.Rule(distance_to_ball['far'] & player_role['middle_blocker'], defensive_position['normal'])
    rule3 = ctrl.Rule(distance_to_position['far'], defensive_position['bad'])
    rule4 = ctrl.Rule(distance_to_ball['close'] & player_role['outside_hitter'], defensive_position['normal'])
    rule5 = ctrl.Rule(distance_to_ball['medium'] & player_role['setter'], defensive_position['normal'])
    rule6 = ctrl.Rule(distance_to_ball['close'] & player_role['middle_blocker'], defensive_position['good'])
    # Puedes agregar más reglas según las necesidades

    # Crear el sistema de control y la simulación
    defensive_position_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
    defensive_positioning = ctrl.ControlSystemSimulation(defensive_position_ctrl)

    return defensive_positioning


def fuzzy_offensive_position():
    # Definir los universos de discurso para las variables de entrada y salida
    distance_to_position = ctrl.Antecedent(np.arange(0, 18.1, 0.1), 'distance_to_position')
    distance_to_ball = ctrl.Antecedent(np.arange(0, 18.1, 0.1), 'distance_to_ball')
    player_role = ctrl.Antecedent(np.arange(0, 5, 1), 'player_role')
    offensive_position = ctrl.Consequent(np.arange(0, 101, 1), 'offensive_position')

    # Definir las funciones de membresía para distance_to_position
    distance_to_position['close'] = fuzz.trimf(distance_to_position.universe, [0, 0, 6])
    distance_to_position['medium'] = fuzz.trimf(distance_to_position.universe, [4, 9, 14])
    distance_to_position['far'] = fuzz.trimf(distance_to_position.universe, [12, 18, 18])

    # Definir las funciones de membresía para distance_to_ball
    distance_to_ball['close'] = fuzz.trimf(distance_to_ball.universe, [0, 0, 6])
    distance_to_ball['medium'] = fuzz.trimf(distance_to_ball.universe, [4, 9, 14])
    distance_to_ball['far'] = fuzz.trimf(distance_to_ball.universe, [12, 18, 18])

    # Definir las funciones de membresía para player_role
    player_role['setter'] = fuzz.trimf(player_role.universe, [0, 0, 0])
    player_role['middle_blocker'] = fuzz.trimf(player_role.universe, [1, 1, 1])
    player_role['outside_hitter'] = fuzz.trimf(player_role.universe, [2, 2, 2])
    player_role['opposite'] = fuzz.trimf(player_role.universe, [3, 3, 3])
    player_role['libero'] = fuzz.trimf(player_role.universe, [4, 4, 4])

    # Definir las funciones de membresía para offensive_position
    offensive_position['bad'] = fuzz.trimf(offensive_position.universe, [0, 0, 50])
    offensive_position['normal'] = fuzz.trimf(offensive_position.universe, [25, 50, 75])
    offensive_position['good'] = fuzz.trimf(offensive_position.universe, [50, 100, 100])

    # Definir las reglas
    rule1 = ctrl.Rule(distance_to_ball['close'] & player_role['setter'], offensive_position['good'])
    rule2 = ctrl.Rule(distance_to_ball['far'] & player_role['libero'], offensive_position['bad'])
    rule3 = ctrl.Rule(distance_to_position['far'], offensive_position['bad'])
    rule4 = ctrl.Rule(distance_to_ball['close'] & player_role['outside_hitter'], offensive_position['good'])
    rule5 = ctrl.Rule(distance_to_ball['medium'] & player_role['middle_blocker'], offensive_position['normal'])
    rule6 = ctrl.Rule(distance_to_ball['close'] & player_role['opposite'], offensive_position['good'])
    # Puedes agregar más reglas según las necesidades

    # Crear el sistema de control y la simulación
    offensive_position_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
    offensive_positioning = ctrl.ControlSystemSimulation(offensive_position_ctrl)

    return offensive_positioning
