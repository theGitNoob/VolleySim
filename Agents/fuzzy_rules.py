import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class DefensivePositionFuzzySystem:
    def __init__(self):
        self.distance_to_position = ctrl.Antecedent(np.arange(0, 18, 1), 'distance_to_position')  # 0-20 metros
        self.distance_to_ball = ctrl.Antecedent(np.arange(0, 18, 1), 'distance_to_ball')  # 0-20 metros
        self.player_role = ctrl.Antecedent(np.arange(0, 5, 1), 'player_role')  # 0-4 roles
        self.defensive_position = ctrl.Consequent(np.arange(0, 101, 1), 'defensive_position')  # 0-100

        self.distance_to_position['low'] = fuzz.trimf(self.distance_to_position.universe, [0, 0, 3])
        self.distance_to_position['medium'] = fuzz.trimf(self.distance_to_position.universe, [2, 7, 11])
        self.distance_to_position['high'] = fuzz.trimf(self.distance_to_position.universe, [10, 18, 18])

        self.distance_to_ball['low'] = fuzz.trimf(self.distance_to_ball.universe, [0, 0, 3])
        self.distance_to_ball['medium'] = fuzz.trimf(self.distance_to_ball.universe, [2, 7, 11])
        self.distance_to_ball['high'] = fuzz.trimf(self.distance_to_ball.universe, [10, 18, 18])

        self.player_role['L'] = fuzz.trimf(self.player_role.universe, [0, 0, 1])
        self.player_role['S'] = fuzz.trimf(self.player_role.universe, [0, 1, 2])
        self.player_role['MB'] = fuzz.trimf(self.player_role.universe, [1, 2, 3])
        self.player_role['OH'] = fuzz.trimf(self.player_role.universe, [2, 3, 4])
        self.player_role['O'] = fuzz.trimf(self.player_role.universe, [3, 4, 4])

        self.defensive_position['bad'] = fuzz.trimf(self.defensive_position.universe, [0, 0, 50])
        self.defensive_position['normal'] = fuzz.trimf(self.defensive_position.universe, [25, 50, 75])
        self.defensive_position['good'] = fuzz.trimf(self.defensive_position.universe, [50, 100, 100])

        self.rules = [
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['L'], self.defensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['S'], self.defensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['MB'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['OH'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['O'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['L'], self.defensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['S'], self.defensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['O'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['L'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['S'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['MB'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['OH'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['O'], self.defensive_position['bad']),

            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['L'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['S'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['MB'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['OH'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['O'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['L'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['S'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['O'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['L'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['S'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['MB'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['OH'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['O'], self.defensive_position['bad']),

            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['L'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['S'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['MB'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['OH'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['O'], self.defensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['L'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['S'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['O'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['L'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['S'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['MB'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['OH'], self.defensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['O'], self.defensive_position['bad']),
        ]

        self.defensive_position_ctrl = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.defensive_position_ctrl)

    def evaluate(self, distance_to_position, distance_to_ball, player_role):
        self.simulation.input['distance_to_position'] = distance_to_position
        self.simulation.input['distance_to_ball'] = distance_to_ball
        self.simulation.input['player_role'] = get_role_number(player_role)

        self.simulation.compute()

        return self.simulation.output['defensive_position']


class OffensivePositionFuzzySystem:
    def __init__(self):
        self.distance_to_position = ctrl.Antecedent(np.arange(0, 21, 1), 'distance_to_position')  # 0-20 metros
        self.distance_to_net = ctrl.Antecedent(np.arange(0, 21, 1), 'distance_to_net')  # 0-20 metros
        self.distance_to_ball = ctrl.Antecedent(np.arange(0, 21, 1), 'distance_to_ball')  # 0-20 metros
        self.player_role = ctrl.Antecedent(np.arange(0, 5, 1), 'player_role')  # 0-4 roles
        self.offensive_position = ctrl.Consequent(np.arange(0, 101, 1), 'offensive_position')  # 0-100

        self.distance_to_position['low'] = fuzz.trimf(self.distance_to_position.universe, [0, 0, 5])
        self.distance_to_position['medium'] = fuzz.trimf(self.distance_to_position.universe, [4, 10, 16])
        self.distance_to_position['high'] = fuzz.trimf(self.distance_to_position.universe, [15, 20, 20])

        self.distance_to_net['close'] = fuzz.trimf(self.distance_to_net.universe, [0, 0, 3])
        self.distance_to_net['medium'] = fuzz.trimf(self.distance_to_net.universe, [2, 5, 8])
        self.distance_to_net['far'] = fuzz.trimf(self.distance_to_net.universe, [7, 20, 20])

        self.distance_to_ball['low'] = fuzz.trimf(self.distance_to_ball.universe, [0, 0, 5])
        self.distance_to_ball['medium'] = fuzz.trimf(self.distance_to_ball.universe, [4, 10, 16])
        self.distance_to_ball['high'] = fuzz.trimf(self.distance_to_ball.universe, [15, 20, 20])

        self.player_role['L'] = fuzz.trimf(self.player_role.universe, [0, 0, 1])
        self.player_role['S'] = fuzz.trimf(self.player_role.universe, [0, 1, 2])
        self.player_role['MB'] = fuzz.trimf(self.player_role.universe, [1, 2, 3])
        self.player_role['OH'] = fuzz.trimf(self.player_role.universe, [2, 3, 4])
        self.player_role['O'] = fuzz.trimf(self.player_role.universe, [3, 4, 4])

        self.offensive_position['bad'] = fuzz.trimf(self.offensive_position.universe, [0, 0, 50])
        self.offensive_position['normal'] = fuzz.trimf(self.offensive_position.universe, [25, 50, 75])
        self.offensive_position['good'] = fuzz.trimf(self.offensive_position.universe, [50, 100, 100])

        self.rules = [
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['L'], self.offensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['S'], self.offensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['MB'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['OH'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['low'] & self.player_role['O'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['L'], self.offensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['S'], self.offensive_position['good']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['medium'] & self.player_role['O'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['L'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['S'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['MB'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['OH'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['low'] & self.distance_to_ball['high'] & self.player_role['O'], self.offensive_position['bad']),

            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['L'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['S'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['MB'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['OH'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['low'] & self.player_role['O'], self.offensive_position['good']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['L'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['S'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['medium'] & self.player_role['O'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['L'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['S'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['MB'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['OH'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['medium'] & self.distance_to_ball['high'] & self.player_role['O'], self.offensive_position['bad']),

            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['L'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['S'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['MB'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['OH'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['low'] & self.player_role['O'], self.offensive_position['normal']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['L'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['S'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['MB'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['OH'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['medium'] & self.player_role['O'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['L'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['S'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['MB'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['OH'], self.offensive_position['bad']),
            ctrl.Rule(self.distance_to_position['high'] & self.distance_to_ball['high'] & self.player_role['O'], self.offensive_position['bad']),
        ]

        self.offensive_position_ctrl = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.offensive_position_ctrl)

    def evaluate(self, distance_to_position, distance_to_net, distance_to_ball, player_role):
        self.simulation.input['distance_to_position'] = distance_to_position
        self.simulation.input['distance_to_net'] = distance_to_net
        self.simulation.input['distance_to_ball'] = distance_to_ball
        self.simulation.input['player_role'] = get_role_number(player_role)

        self.simulation.compute()

        return self.simulation.output['offensive_position']


def get_role_number(role):
    if role == 'L':
        return 0
    if role == 'S':
        return 1
    if role == 'MB':
        return 2
    if role == 'OH':
        return 3
    if role == 'O':
        return 4
    return -1
