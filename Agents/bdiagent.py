from typing import Dict, Tuple, List

from Agents.actions import Action, Attack, Block, Move, Serve, Set, Nothing, Receive
from Agents.player_agent import Player
from Tools.enum import T1, T2
from Tools.game import Game


class VolleyballPerception:
    def __init__(
            self,
            team_score=0,
            opponent_score=0,
            ball_possession=None,
            last_player_touched=None,
            serving_player=None,
            serving_team=None,
            serve_done=False,
            ball_position=None,
            team_players_positions=None,  # The players position in the same team {player_id: position}
            opponent_players_positions=None,  # The players position in the opponent team {player_id: position}
            my_team=None,
            opponent_team=None,
            team_touches=0,
            front_row=False,
            can_block=False,
            distance_to_ball=None,
            last_team_touched=None
    ) -> None:
        self.can_block = can_block
        self.front_row = front_row
        self.team_touches = team_touches
        self.my_team = my_team
        self.opponent_players_positions = opponent_players_positions
        self.team_players_positions = team_players_positions
        self.serve_done = serve_done
        self.serving_team = serving_team
        self.last_player_touched = last_player_touched
        self.serving_player = serving_player
        self.ball_possession = ball_possession
        self.ball_position = ball_position
        self.opponent_team = opponent_team
        self.opponent_score = opponent_score
        self.team_score = team_score
        self.distance_to_ball = distance_to_ball
        self.last_team_touched = last_team_touched

    def __str__(self):
        return (
            f"\n VolleyballPerception:\n"
            f"  Team score: {self.team_score}\n"
            f"  Opponent score: {self.opponent_score}\n"
            f"  Ball possession: {self.ball_possession}\n"
            f"  Last player touched: {self.last_player_touched}\n"
            f"  Serving player: {self.serving_player}\n"
            f"  Serving team: {self.serving_team}\n"
            f"  Serve done: {self.serve_done}\n"
            f"  Ball position: {self.ball_position}\n"
            f"  Team players positions: {self.team_players_positions}\n"
            f"  Opponent players positions: {self.opponent_players_positions}\n"
            f"  My team: {self.my_team}\n"
            f"  Opponent team: {self.opponent_team}\n"
        )


class BdiAgent(Player):
    def __init__(
            self,
            dorsal: int,
            team: str,
            rules,
            active_rules,
            base_beliefs=None,
    ):
        super().__init__(dorsal, team, None)
        if base_beliefs is None:
            base_beliefs = {}
        self.rules = rules
        self.active_rules = active_rules
        self.game = None
        self.perception = VolleyballPerception()
        #### Base Beliefs ####
        self.beliefs = {
            "team_players_positions": {
            },
            "opponent_players_positions": {
            },
            "ball_position": None,  # self.perception.ball_position,
            "opponent_strategy": None,  # self.perception.opponent_strategy,
            "team_score": None,
            "opponent_score": None,
            "active_rules": self.active_rules,
            "rules": self.rules,
            "serve_done": False,
            "serving_team": None,
            "serving_player": None,
            "my_team": None,
            "opponent_team": None,
            "team_touches": 0,
            "can_block": False,
            "front_row": False,
            "distance_to_ball": None,
            "last_player_touched": None,
            "last_team_touched": None,

            "team_good_attackers": [],
            "opponent_bad_receivers": [],
        }
        self.beliefs = {key: base_beliefs[key] if key in base_beliefs else self.beliefs[key] for key in self.beliefs}

        # Each desire must be a list of tuples (bool, weight,destiny)
        self.desires = {
            "move_player": [],
            "set_ball": [],
            "attack": [],
            "block": [],
            "serve": [],
            "receive": [],
            "do_nothing": [],
        }

        self.intentions = {
            "move_player": [],
            "set_ball": [],
            "attack": [],
            "block": [],
            "serve": [],
            "receive": [],
            "do_nothing": [],
        }

        """
        BDI flow
        1. Get Perceptions
        2. BRF
        3. Generate Desires
        4. Generate Intentions
        5. Execute Intentions

        - A belief can generate multiple desires.
        - Each desire can be converted to an intention.
        - Each belief can be active or inactive.
        - Only an active belief can generate desires.

        - Get Perceptions: The agent perceives the current state of the game.
        - BRF: The agent updates its beliefs based on the current state of the game.
        - Generate Desires: The agent generates its desires based on its beliefs. Each desire is associated with a belief.
        - Generate Intentions: The agent generates its intentions based on its desires. Only one intention can be active at a time.
        """

    def update_perceptions(self, game: Game) -> VolleyballPerception:
        """
        Retrieve the current perceptions of the game for the agent.

        Args:
            game (Game): The current game state.

        Returns:
            Dict: A dictionary containing the agent's perceptions.
        """
        self.game = game
        perceptions = {
            "team_score": game.t1_score if self.team == T1 else game.t2_score,
            "opponent_score": game.t2_score if self.team == T1 else game.t1_score,
            "ball_possession": game.ball_possession_team,
            "last_player_touched": game.last_player_touched,
            "serving_player": game.serving_player().player,
            "serving_team": game.serving_team,
            "serve_done": game.serve_done(),
            "ball_position": (game.field.find_ball().row, game.field.find_ball().col),
            "team_players_positions": {
                player: (game.field.find_player(player, self.team).row, game.field.find_player(player, self.team).col)
                for player in (game.t1.on_field if T1 == self.team else game.t2.on_field)
            },
            "opponent_players_positions": {
                player: (game.field.find_player(player, T1 if self.team == T2 else T2).row,
                         game.field.find_player(player, T1 if self.team == T2 else T2).col)
                for player in (game.t1.on_field if T2 == self.team else game.t2.on_field)
            },
            "my_team": self.team,
            "opponent_team": T1 if self.team == T2 else T2,
            "team_touches": game.touches[self.team],
            "front_row": game.is_front_row(self.dorsal, self.team),
            "can_block": game.can_block(),
            "distance_to_ball": game.field.distance(
                (game.field.find_ball().row, game.field.find_ball().col),
                (game.field.find_player(self.dorsal, self.team).row,
                 game.field.find_player(self.dorsal, self.team).col),
            ),
            "last_team_touched": game.last_team_touched

        }
        return VolleyballPerception(**perceptions)

    def brf(self, game, verbose: bool = False):
        """
        Update beliefs based on perceptions.
        """
        self.perception = self.update_perceptions(game)

        self.beliefs["team_players_positions"] = self.perception.team_players_positions
        self.beliefs["opponent_players_positions"] = self.perception.opponent_players_positions
        self.beliefs["ball_position"] = self.perception.ball_position
        self.beliefs["team_score"] = self.perception.team_score
        self.beliefs["opponent_score"] = self.perception.opponent_score
        self.beliefs["ball_possession"] = self.perception.ball_possession
        self.beliefs["last_player_touched"] = self.perception.last_player_touched
        self.beliefs["serving_player"] = self.perception.serving_player
        self.beliefs["serving_team"] = self.perception.serving_team
        self.beliefs["serve_done"] = self.perception.serve_done
        self.beliefs["my_team"] = self.perception.my_team
        self.beliefs["opponent_team"] = self.perception.opponent_team
        self.beliefs["team_touches"] = self.perception.team_touches
        self.beliefs["front_row"] = self.perception.front_row
        self.beliefs["can_block"] = self.perception.can_block
        self.beliefs["distance_to_ball"] = self.perception.distance_to_ball
        self.beliefs["last_team_touched"] = self.perception.last_team_touched

        if verbose:
            print("Updated beliefs:")
            for item, value in self.beliefs.items():
                print(f"{item}: {value}")

    def generate_desires(self):
        """
        Generate desires based on beliefs and goals.
        """

        # Clean all desires
        for desire in self.desires:
            self.desires[desire] = []

        for rule_id in self.beliefs['active_rules']:
            self.rules[rule_id].evaluate(self)

    def generate_intentions(self):
        """
        Convert  only active desires into intentions.
        """
        self.intentions['move_player'] = [(i[1], i[2]) for i in self.desires['move_player'] if i[0]]
        self.intentions['move_player'].sort(key=lambda x: x[1], reverse=True)
        self.intentions['move_player'] = self.intentions['move_player'][0] if len(
            self.intentions['move_player']) > 0 else []

        self.intentions["set_ball"] = [(i[1], i[2]) for i in self.desires["set_ball"] if i[0]]
        self.intentions["set_ball"].sort(key=lambda x: x[1], reverse=True)
        self.intentions['set_ball'] = self.intentions['set_ball'][0] if len(self.intentions['set_ball']) > 0 else None

        self.intentions["attack"] = [(i[1], i[2]) for i in self.desires["attack"] if i[0]]
        self.intentions["attack"].sort(key=lambda x: x[1], reverse=True)
        self.intentions['attack'] = self.intentions['attack'][0] if len(self.intentions['attack']) > 0 else None

        self.intentions["block"] = [(i[1], i[2]) for i in self.desires["block"] if i[0]]
        self.intentions["block"].sort(key=lambda x: x[1], reverse=True)
        self.intentions['block'] = self.intentions['block'][0] if len(self.intentions['block']) > 0 else None

        self.intentions["serve"] = [(i[1], i[2]) for i in self.desires["serve"] if i[0]]
        self.intentions["serve"].sort(key=lambda x: x[1], reverse=True)
        self.intentions['serve'] = self.intentions['serve'][0] if len(self.intentions['serve']) > 0 else None

        self.intentions["receive"] = [(i[1], i[2]) for i in self.desires["receive"] if i[0]]
        self.intentions["receive"].sort(key=lambda x: x[1], reverse=True)
        self.intentions['receive'] = self.intentions['receive'][0] if len(self.intentions['receive']) > 0 else None

        self.intentions['do_nothing'] = [(i[1], i[2]) for i in self.desires['do_nothing'] if i[0]]
        self.intentions['do_nothing'].sort(key=lambda x: x[1], reverse=True)
        self.intentions['do_nothing'] = self.intentions['do_nothing'][0] if len(
            self.intentions['do_nothing']) > 0 else None

    def execute_intentions(self) -> Action:
        """
        Execute the intentions.
        """
        actions: List[Tuple[Action, int]] = [
            (Nothing(self.dorsal, self.team, self.game), self.intentions["do_nothing"][0])]

        if self.intentions["move_player"] is not None:
            # Logic to move player
            player_id = self.dorsal
            target_position = self.intentions["move_player"][1]
            player_position = self.beliefs['team_players_positions'][player_id]
            actions.append((
                Move(
                    player_position,
                    target_position,
                    player_id,
                    self.team,
                    self.game,
                ),
                self.intentions["move_player"][0])
            )

        if self.intentions["set_ball"] is not None:
            # Logic to pass ball
            target_position = self.intentions['set_ball'][1]
            ball_position = self.beliefs["ball_position"]
            actions.append(
                (Set(
                    ball_position,
                    target_position,
                    self.dorsal,
                    self.team,
                    self.game,
                ),
                 self.intentions["set_ball"][0]
                )
            )

        if self.intentions["attack"] is not None:
            # Logic to attack ball
            player_id = self.dorsal
            target_position = self.intentions["attack"][1]

            actions.append(
                (Attack(
                    self.beliefs['ball_position'],
                    target_position,
                    player_id,
                    self.team,
                    self.game,
                ),
                 self.intentions["attack"][0]
                )
            )

        if self.intentions["block"] is not None:
            # Logic to block
            ball_position = self.beliefs["ball_position"]
            target_position = self.intentions["block"][1]
            actions.append(
                (
                    Block(
                        ball_position,
                        target_position,
                        self.dorsal,
                        self.team,
                        self.game,
                    ),
                    self.intentions["block"][0]
                )
            )

        if self.intentions["serve"] is not None:
            # Logic to serve
            player_id = self.dorsal
            ball_position = self.beliefs["ball_position"]
            target_position = self.intentions["serve"][1]
            actions.append((
                Serve(
                    ball_position,
                    target_position,
                    player_id,
                    self.team,
                    self.game,
                ),
                self.intentions["serve"][0]
            )
            )

        if self.intentions["receive"] is not None:
            # Logic to receive the ball
            player_id = self.dorsal
            ball_position = self.beliefs["ball_position"]
            target_position = self.intentions["receive"][1]
            actions.append(
                (
                    Receive(
                        ball_position,
                        target_position,
                        player_id,
                        self.team,
                        self.game,
                    ),
                    self.intentions["receive"][0]
                )
            )

        actions.sort(key=lambda x: x[1], reverse=True)

        return actions[0][0]

    def play(self, simulator) -> Action:
        self.brf(simulator.game)
        self.generate_desires()
        self.generate_intentions()
        return self.execute_intentions()


class Rule:
    def __init__(self, rule_id: str, weight: int, description):
        self.id = rule_id
        self.weight = weight
        self.description = description

    def evaluate(self, agent):
        pass


class CoreRule(Rule):
    def __init__(self, id, weight, description, desires, conditions):
        super().__init__(id, weight, description)
        self.desires = desires
        self.conditions = conditions

    def evaluate(self, agent: BdiAgent):
        # Evaluate if all conditions are met and activate desires
        for condition in self.conditions:
            if not condition(agent.beliefs):
                return
        for desire in self.desires:
            agent.desires[desire] = True


class MovePlayerRule(Rule):
    def __init__(self):
        super().__init__(
            "MovePlayer", 2, "Move player to a better position if the ball is far"
        )

    def evaluate(self, agent: BdiAgent):
        agent.desires["move_player"].append(([True, self.weight, (0, 0)]))


class DoNothingRule(Rule):
    def __init__(self):
        super().__init__(
            "DoNothing", 1, "Do nothing"
        )

    def evaluate(self, agent: BdiAgent):
        agent.desires["do_nothing"].append((True, self.weight, (0, 0)))


class SetBallRule(Rule):
    def __init__(self):
        super().__init__(
            "SetBall", 3, "Pass the ball to a teammate if in a bad position to attack"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_position"] and agent.beliefs['serve_done'] and agent.beliefs['team_touches'] == 1 and \
                agent.beliefs['ball_possession'] == agent.team and agent.beliefs[
            'distance_to_ball'] <= 2 and (agent.beliefs["last_player_touched"] != agent.dorsal if agent.beliefs[
                                                                                                      "last_team_touched"] == agent.team else True):
            agent.desires["set_ball"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["set_ball"].append((False, self.weight))


class AttackRule(Rule):
    def __init__(self):
        super().__init__("Attack", 3, "Attack if in a good position near the net")

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_possession"] == agent.team and agent.beliefs["serve_done"] and agent.beliefs[
            "team_touches"] > 1 and agent.beliefs["distance_to_ball"] < 2 and (agent.beliefs[
                                                                                   "last_player_touched"] != agent.dorsal if
        # TODO:
        agent.beliefs[
            "last_team_touched"] == agent.team else True):
            agent.desires["attack"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["attack"].append((False, self.weight))


class BlockRule(Rule):
    def __init__(self):
        super().__init__(
            "Block", 3, "Block if the opponent is about to attack the ball"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_possession"] == agent.team and agent.beliefs["serve_done"] and agent.beliefs[
            "team_touches"] == 0 and agent.beliefs["front_row"] and agent.beliefs["can_block"] and agent.beliefs[
            'distance_to_ball'] <= 2:
            agent.desires["block"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["block"].append((False, self.weight))


class ServeRule(Rule):
    def __init__(self):
        super().__init__("Serve", 10, "Serve the ball if it's the team's turn to serve")

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["serving_player"] == agent.dorsal and agent.beliefs['serving_team'] == agent.team and \
                agent.beliefs['serve_done'] == False:
            agent.desires["serve"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["serve"].append((False, self.weight))


class ServeToBadReceiversRule(Rule):
    def __init__(self):
        super().__init__(
            "ServeToBadReceivers", 11, "Serve to players who are bad at receiving"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["serve_done"] == False and agent.beliefs["serving_team"] == agent.team and agent.beliefs[
            "serving_player"] == agent.dorsal \
                and len(agent.beliefs["opponent_bad_receivers"]) > 0:
            agent.desires["serve"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["serve"].append((False, self.weight))


class SetBallToGoodAttackersRule(Rule):
    def __init__(self):
        super().__init__(
            "SetBallToGoodAttackers", 5, "Pass the ball to players who are good at attacking"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_possession"] == agent.team and agent.beliefs["serve_done"] and agent.beliefs[
            "team_touches"] == 1 and len(agent.beliefs["team_good_attackers"]) > 0 and agent.beliefs[
            'distance_to_ball'] <= 2 and (agent.beliefs["last_player_touched"] != agent.dorsal if agent.beliefs[
                                                                                                      "last_team_touched"] == agent.team else True):
            agent.desires["set_ball"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["set_ball"].append((False, self.weight))


class AttackToBadReceiversRule(Rule):
    def __init__(self):
        super().__init__(
            "AttackToBadReceivers", 4, "Attack to players who are bad at receiving"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_possession"] == agent.team and agent.beliefs["serve_done"] and agent.beliefs[
            "team_touches"] > 1 and len(agent.beliefs["opponent_bad_receivers"]) > 0 and (agent.beliefs[
                                                                                              "last_player_touched"] != agent.dorsal if
        agent.beliefs[
            "last_team_touched"] == agent.team else True):
            agent.desires["attack"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["attack"].append((False, self.weight))


class ReceiveRule(Rule):
    def __init__(self):
        super().__init__(
            "Receive", 3, "Receive the ball"
        )

    def evaluate(self, agent: BdiAgent):
        if agent.beliefs["ball_possession"] == agent.team and agent.beliefs["serve_done"] and agent.beliefs[
            "team_touches"] == 0 and agent.beliefs[
            'distance_to_ball'] <= 2 and (agent.beliefs["last_player_touched"] != agent.dorsal if agent.beliefs[
                                                                                                      "last_team_touched"] == agent.team else True):
            agent.desires["receive"].append((True, self.weight, (0, 0)))
        else:
            agent.desires["receive"].append((False, self.weight))


base_rules = {
    "DoNothing": DoNothingRule(),
    "MovePlayer": MovePlayerRule(),
    "SetBall": SetBallRule(),
    "AttackBall": AttackRule(),
    "Block": BlockRule(),
    "Serve": ServeRule(),
    "ServeToBadReceivers": ServeToBadReceiversRule(),
    "AttackToBadReceivers": AttackToBadReceiversRule(),
    "SetBallToGoodAttackers": SetBallToGoodAttackersRule(),
    "Receive": ReceiveRule(),
}

base_active_rules = [
    "DoNothing",
    "MovePlayer",
    "SetBall",
    "AttackBall",
    "Block",
    "Serve",
    "ServeToBadReceivers",
    "AttackToBadReceivers",
    "SetBallToGoodAttackers",
    "Receive",
]

base_beliefs_t1 = {
    "team_good_attackers": [180],
    "opponent_bad_receivers": [180],
}
