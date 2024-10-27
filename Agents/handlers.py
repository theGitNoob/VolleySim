# handlers.py

from Agents.actions import Action, Attack, Nothing
from .desire_handler import DesireHandler
from .intention_handler import IntentionHandler


######## Desire Handlers ########
class AttackBadReceiverDesireHandler(DesireHandler):
    def generate_desires(self, agent):
        pass


class ServeToBadReceiverDesireHandler(DesireHandler):
    def generate_desires(self, agent):
        pass


class PassToGoodAttackerDesireHandler(DesireHandler):
    def generate_desires(self, agent):
        pass


######## Intention Handlers ########
class AttackBadReceiverIntentionHandler(IntentionHandler):

    def get_action(self, agent) -> Action:
        bad_receiver = agent.get_belief("bad_receiver")
        if bad_receiver:
            bad_receiver_dorsal = bad_receiver["value"]
            if bad_receiver_dorsal is not None:
                return Attack(
                    src=agent.game.field.find_player(agent.dorsal, agent.team),
                    dest=agent.game.field.find_player(bad_receiver_dorsal),
                    player=bad_receiver_dorsal,
                    team=agent.team,
                    game=agent.game,
                )
        return Nothing(agent.dorsal, "", agent.game)


class ServeToBadReceiveIntentionHandler(IntentionHandler):
    def get_action(self, agent) -> Action:
        if "serve_to_bad_receiver" in agent.intentions.get_intentions():
            bad_receiver = agent.beliefs.get_belief("bad_receiver")
            if bad_receiver:
                bad_receiver_dorsal = bad_receiver
                return Attack(
                    src=agent.game.field.find_player(agent.dorsal),
                    dest=agent.game.field.find_player(bad_receiver_dorsal),
                    player=bad_receiver_dorsal,
                    team=agent.team,
                    game=agent.game,
                )


class PassToGoodAttackerIntentionHandler(IntentionHandler):
    def get_action(self, agent) -> Action:
        if "pass_to_good_attacker" in agent.intentions.get_intentions():
            good_attacker = agent.beliefs.get_belief("good_attacker")
            if good_attacker:
                good_attacker_dorsal = good_attacker
                return Attack(
                    src=agent.game.field.find_player(agent.dorsal),
                    dest=agent.game.field.find_player(good_attacker_dorsal),
                    player=good_attacker_dorsal,
                    team=agent.team,
                    game=agent.game,
                )
