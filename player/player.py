import random

class Player:
    def __init__(self, altura, resistencia, salto_maximo, velocidad):
        self.altura = altura
        self.resistencia = resistencia
        self.salto_maximo = salto_maximo
        self.velocidad = velocidad
        self.current_resistencia = resistencia
    
    def update_resistance(self, decrease_amount):
        self.current_resistencia = max(0, self.current_resistencia - decrease_amount)
        self.salto_maximo = self.salto_maximo * (self.current_resistencia / self.resistencia)
        self.velocidad = self.velocidad * (self.current_resistencia / self.resistencia)

class Actions:
    @staticmethod
    def pass_ball(player: Player):
        # The effectiveness of the pass is influenced by the player’s speed and resistance.
        pass_quality = player.velocidad * (player.current_resistencia / player.resistencia)
        
        # Introduce some randomness to simulate real-world conditions.
        pass_success = pass_quality > random.uniform(0.4, 0.8)
        
        player.update_resistance(2)  # Passing reduces resistance slightly.
        
        if pass_success:
            return "Successful pass!"
        else:
            return "The pass was inaccurate."

    @staticmethod
    def block_ball(player: Player):
        # Blocking effectiveness is influenced by height and jump.
        block_height = player.altura + player.salto_maximo
        block_success = block_height > random.uniform(2.4, 3.0)  # Comparing against an average attack height.

        player.update_resistance(3)  # Blocking is more taxing and reduces resistance more.

        if block_success:
            return "Successful block!"
        else:
            return "The block failed to stop the ball."

    @staticmethod
    def shoot_ball(player: Player):
        # Shooting/spiking effectiveness is influenced by jump and resistance.
        spike_power = player.salto_maximo * (player.current_resistencia / player.resistencia)
        spike_success = spike_power > random.uniform(0.6, 1.2)

        player.update_resistance(4)  # Spiking is physically demanding and reduces resistance more.

        if spike_success:
            return "Powerful spike! Point scored."
        else:
            return "The spike was blocked or went out of bounds."

# Example usage:
player = Player(altura=1.9, resistencia=100, salto_maximo=0.6, velocidad=5.5)

# Perform actions
print(Actions.pass_ball(player))
print(Actions.block_ball(player))
print(Actions.shoot_ball(player))