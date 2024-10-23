from typing import List, TypedDict, Any

from Agents.actions import Action
from Agents.desire_handler import DesireHandler
from Agents.handlers import AttackBadReceiverDesireHandler, ServeToBadReceiverDesireHandler, \
    PassToGoodAttackerDesireHandler, AttackBadReceiverIntentionHandler, ServeToBadReceiveIntentionHandler, \
    PassToGoodAttackerIntentionHandler
from Agents.intention_handler import IntentionHandler
from Agents.player_agent import Player
from Tools.game import Game


class Belief(TypedDict):
    name: str
    value: Any
    active: bool
    # The handler is the class that will handle the belief, typically generating desires


class Desire(TypedDict):
    name: str
    handler: DesireHandler | None


class Intention(TypedDict):
    name: str
    priority: int
    handler: IntentionHandler | None


class BdiAgent(Player):
    def __init__(self, dorsal: int, team: str):
        super().__init__(dorsal, team, None)

        #### Base Beliefs ####
        self.game = None
        self.beliefs = [
            Belief(name="bad_receiver", value=None, active=False),
            Belief(name="ball_possession", value=None, active=False),  # This is also an assertion
            Belief(name="ball_location", value=None, active=False),  # This is also an assertion
            Belief(name="good_attacker", value=None, active=False),
            Belief(name="good_defender", value=None, active=False),
        ]

        #### Base Desires ####
        self.desires = [
            Desire(
                name="attack_bad_receiver",
                handler=AttackBadReceiverDesireHandler("attack_bad_receiver"),
            ),
            Desire(
                name="serve_to_bad_receiver",
                handler=ServeToBadReceiverDesireHandler("serve_to_bad_receiver"),
            ),
            Desire(
                name="pass_to_good_attacker",
                handler=PassToGoodAttackerDesireHandler("pass_to_good_attacker"),
            ),
        ]

        #### Base Intentions ####
        self.intentions = [
            Intention(
                name="attack_bad_receiver",
                handler=AttackBadReceiverIntentionHandler("attack_bad_receiver"),
                priority=1,
            ),
            Intention(
                name="serve_to_bad_receiver",
                handler=ServeToBadReceiveIntentionHandler("serve_to_bad_receiver"),
                priority=2,
            ),
            Intention(
                name="pass_to_good_attacker",
                handler=PassToGoodAttackerIntentionHandler("pass_to_good_attacker"),
                priority=3,
            ),
        ]

        self.desires_handlers: List[DesireHandler] = [
            AttackBadReceiverDesireHandler("attack_bad_receiver"),
            ServeToBadReceiverDesireHandler("serve_to_bad_receiver"),
            PassToGoodAttackerDesireHandler("pass_to_good_attacker"),
        ]
        self.intentions_handlers: List[IntentionHandler] = [

            PassToGoodAttackerIntentionHandler("attack_bad_receiver"),
            PassToGoodAttackerIntentionHandler("serve_to_bad_receiver"),
            PassToGoodAttackerIntentionHandler("pass_to_good_attacker"),
        ]

        # self.game: Game = game
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

    def brf(self, game: Game, verbose: bool = False):
        """
        La función de revisión de creencias actualiza las creencias del agente
        basadas en el estado actual del juego.
        """
        # Obtener percepciones del juego
        perceptions = self.get_perceptions(game)
        self.game = game

        # Actualizar creencias basadas en percepciones
        for belief in self.beliefs:
            name = belief['name']

            if name == 'bad_receiver':
                # Supongamos que perceptions['bad_receivers'] es una lista de jugadores malos para recibir
                bad_receivers = perceptions.get('bad_receivers', [])
                belief['value'] = bad_receivers
                belief['active'] = len(bad_receivers) > 0

            elif name == 'ball_possession':
                # Supongamos que perceptions['ball_possession'] es el jugador que tiene la pelota
                ball_possession = perceptions.get('ball_possession', None)
                belief['value'] = ball_possession
                belief['active'] = ball_possession is not None

            elif name == 'ball_location':
                # Supongamos que perceptions['ball_location'] es la posición actual de la pelota
                ball_location = perceptions.get('ball_location', None)
                belief['value'] = ball_location
                belief['active'] = ball_location is not None

            elif name == 'good_attacker':
                # Supongamos que perceptions['good_attackers'] es una lista de buenos atacantes
                good_attackers = perceptions.get('good_attackers', [])
                belief['value'] = good_attackers
                belief['active'] = len(good_attackers) > 0

            elif name == 'good_defender':
                # Supongamos que perceptions['good_defenders'] es una lista de buenos defensores
                good_defenders = perceptions.get('good_defenders', [])
                belief['value'] = good_defenders
                belief['active'] = len(good_defenders) > 0

            else:
                self.beliefs.append(Belief(name=name, value=None, active=False))

            if verbose:
                print(f"Creencia actualizada '{name}': valor={belief['value']}, activa={belief['active']}")

    def generate_desires(self):
        """
        Genera los deseos del agente basados en sus creencias actuales.
        """
        self.desires = []

        for belief in self.beliefs:
            if belief['active']:
                if belief['name'] == 'bad_receiver':
                    handler1 = self.get_desire_handler_by_name('attack_bad_receiver')
                    if handler1:
                        desire1 = Desire(name='attack_bad_receiver', handler=handler1)
                        self.desires.append(desire1)

                    handler2 = self.get_desire_handler_by_name('serve_to_bad_receiver')
                    if handler2:
                        desire2 = Desire(name='serve_to_bad_receiver', handler=handler2)
                        self.desires.append(desire2)

                elif belief['name'] == 'good_attacker':
                    handler = self.get_desire_handler_by_name('pass_to_good_attacker')
                    if handler:
                        desire = Desire(name='pass_to_good_attacker', handler=handler)
                        self.desires.append(desire)
                else:
                    self.desires.append(Desire(name=belief['name'], handler=None))

    def generate_intentions(self):
        """
        Generates intentions based on the current desires.

        This method iterates over the list of desires and for each desire, it retrieves
        the corresponding intention handler by the desire's name. It then creates an
        Intention object with the desire's name and the retrieved handler, and appends
        it to the list of intentions.


        """
        for desire in self.desires:
            handler = self.get_intention_handler_by_name(desire["name"])
            self.intentions.append(Intention(name=desire["name"], handler=handler, priority=1))

    def add_belief(self, belief: Belief):
        """
        Adds a belief to the agent's list of beliefs.

        Args:
            belief (Belief): The belief to be added to the agent's beliefs.
        """
        self.beliefs.append(belief)

    def add_desire(self, desire: Desire):
        """
        Adds a new desire to the agent's list of desires.

        Args:
            desire (Desire): The desire to be added to the agent's desires list.
        """
        self.desires.append(desire)

    def add_intention(self, intention: Intention):
        """
        Adds an intention to the agent's list of intentions.

        Args:
            intention (Intention): The intention to be added.
        """
        self.intentions.append(intention)

    def execute_intentions(self) -> Action:
        """
        Executes the highest priority intention from the agent's list of intentions.

        The intentions are sorted based on their priority, and the action associated
        with the highest priority intention is executed.

        Returns:
            Action: The action resulting from executing the highest priority intention.
        """
        self.intentions.sort(key=lambda x: x["priority"])
        return self.intentions[0]["handler"].get_action(self)

    def get_belief(self, name: str) -> Belief | None:
        """
        Retrieve a belief by its name.

        Args:
            name (str): The name of the belief to retrieve.

        Returns:
            Belief | None: The belief with the specified name if found, otherwise None.
        """
        for belief in self.beliefs:
            if belief["name"] == name:
                return belief
        return None

    def get_desire_handler_by_name(self, name: str) -> DesireHandler | None:
        """
        Retrieve a list of DesireHandler objects that match the given desire name.

        Args:
            name (str): The name of the desire to match.

        Returns:
            DesireHandler | None: The desire handler with the specified name if found, otherwise None.
            
        """
        for handler in self.desires_handlers:
            if handler.desire_name == name:
                return handler
        return None

    def get_intention_handler_by_name(self, name: str) -> IntentionHandler | None:
        """
        Retrieve an intention handler by its name.

        This method iterates over the list of intention handlers and returns the handler
        whose intention name matches the provided name.

        Args:
            name (str): The name of the intention to match.

        Returns:
            IntentionHandler | None: The intention handler with the specified name if found, otherwise None.
        """

        for handler in self.intentions_handlers:
            if handler.intention_name == name:
                return handler
        return None

    def play(self, simulator):
        """
        Executes the agent's decision-making process in the given simulator.

        This method performs the following steps:
        1. Retrieves the agent's current perceptions.
        2. Updates the agent's beliefs based on the perceptions.
        3. Generates the agent's desires based on the updated beliefs.
        4. Generates the agent's intentions based on the desires.
        5. Executes the agent's intentions and returns the result.

        Args:
            simulator (SimulatorAgent): The simulator in which the agent is operating.

        Returns:
            The result of executing the agent's intentions.
        """
        self.brf(simulator.game)
        self.generate_desires()
        self.generate_intentions()
        return self.execute_intentions()
