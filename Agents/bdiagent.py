from Agents.actions import Action
from Tools.game import Game
from .beliefs import GameState
from .desires import MaintainDefense, ExecuteOffense, ReturnToPosition, Desire
from .intentions import DefenseIntention, OffenseIntention, ReturnToPositionIntention
from .behavior import Defensive, Ofensive, ReturnToPosition, RandomBehavior
from typing import List, Callable


class BdiAgent:
    def __init__(self, game):
        self.game_state = GameState(game)
        self.desires = [ExecuteOffense(), MaintainDefense(), ReturnToPosition()]
        self.intentions = {
            'MaintainDefense': DefenseIntention(),
            'ExecuteOffense': OffenseIntention(),
            'ReturnToPosition': ReturnToPositionIntention()
        }
        self.behaviors = {
            'MaintainDefense': [Defensive(1.8), ReturnToPosition(0.5), Ofensive(0.2), RandomBehavior(0.1)],
            'ExecuteOffense': [Ofensive(1.8), ReturnToPosition(0.5), Defensive(0.2), RandomBehavior(0.1)],
            'ReturnToPosition': [ReturnToPosition(1.0)]
        }

    def select_action(self, possible_actions: Callable[[Game], List[Action]], team:str) -> Action:
        self.game_state.update_beliefs()
        applicable_desires = self.determine_desires(team)
        selected_desire = self.select_desire(applicable_desires)
        intention = self.intentions[selected_desire.name]
        behaviors = self.behaviors[selected_desire.name]
        actions = possible_actions(self.game_state.game)
        return intention.select_action(behaviors, self.game_state, actions)

    def determine_desires(self, team: str) -> List:
        desires = []
        if self.game_state.ball_position.team == team:
            desires.append(self.desires[0])
        else:
            desires.append(self.desires[1])
        desires.append(self.desires[2])
        return sorted(desires, key=lambda d: d.importance, reverse=True)

    def select_desire(self, desires: List) -> Desire:
        return desires[0] if desires else self.desires[-1]
