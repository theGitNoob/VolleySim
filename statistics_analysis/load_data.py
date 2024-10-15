import json


class SimulationAnalyzer:
    def __init__(self, file_path) -> None:
        self.name = file_path.split('/')[-1].split('.')[0]
        self.file_path = file_path
        self.load_data()
        self.games = []
        self.data = None

    def load_data(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        self.data = data

    def analyze(self):
        for game_data in self.data.values():
            self.analyze_game(game_data)

            t1, t2 = self.analyze_game(game_data)
            self.games.append(GameDataAnalyzer(t1, t2))

    @staticmethod
    def analyze_game(game_data):
        t1_data = TeamDataAnalyzer(game_data['t1'])
        t2_data = TeamDataAnalyzer(game_data['t2'])
        return t1_data, t2_data


class GameDataAnalyzer:
    def __init__(self, t1_data, t2_data):
        self.t1_data = t1_data
        self.t2_data = t2_data


class TeamDataAnalyzer:
    def __init__(self, team_data):
        self.player_statistics = team_data['players_statistics']
        self.digs = team_data['statistics']['digs']
        self.serves = team_data['statistics']['serves']
        self.blocks = team_data['statistics']['blocks']
        self.attacks = team_data['statistics']['attacks']
        self.aces = team_data['statistics']['aces']
        self.errors = team_data['statistics']['errors']
        self.points = team_data['statistics']['points']
        self.substitutions = team_data['statistics']['substitutions']
        self.team_data = team_data
