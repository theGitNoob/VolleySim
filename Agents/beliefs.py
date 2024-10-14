from Tools.enum import T1, T2


class PlayerPosition:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class BallPosition:
    def __init__(self, team, row, col):
        self.team = team
        self.row = row
        self.col = col


class GameState:
    def __init__(self, game):
        self.ball_position = None
        self.player_roles = None
        self.game = game
        self.update_beliefs()

    def update_beliefs(self):
        ball_position = self.game.field.find_ball()
        self.ball_position = BallPosition(
            team=self.game.ball_possession_team,
            row=ball_position.row,
            col=ball_position.col
        )
        t1_on_field = set()
        for player in self.game.t1.on_field:
            t1_on_field.add((player, T1))
        t2_on_field = set()
        for player in self.game.t2.on_field:
            t2_on_field.add((player, T2))
        all_players = t1_on_field | t2_on_field
        self.player_roles = {
            player: self.game.t1.get_player_role(player[0]) if player[1] == T1 else self.game.t2.get_player_role(player[0])
            for player in all_players
        }
