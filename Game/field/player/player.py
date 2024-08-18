import random



class Player:
    def __init__(self,id, altura, resistencia, salto_maximo, velocidad):
        self.id=id
        self.altura = altura
        self.resistencia = resistencia
        self.salto_maximo = salto_maximo
        self.velocidad = velocidad
        self.current_resistencia = resistencia
    
    def update_resistance(self, decrease_amount):
        self.current_resistencia = max(0, self.current_resistencia - decrease_amount)
        self.salto_maximo = self.salto_maximo * (self.current_resistencia / self.resistencia)
        self.velocidad = self.velocidad * (self.current_resistencia / self.resistencia)
    def takeAction(self,actionList:list,game):
        random_index=random.randint(0,len(actionList)-1)
        action_to_make= actionList[random_index] #escoge una accion al azar de una lista de acciones qe se le pase
        return action_to_make(self,game)
        


class Action:
    @staticmethod
    def pass_ball(player: Player,game):
        # The effectiveness of the pass is influenced by the player’s speed and resistance.
        pass_quality = player.velocidad * (player.current_resistencia / player.resistencia)
        
        # Introduce some randomness to simulate real-world conditions.
        pass_success = pass_quality > random.uniform(0.4, 0.8)
        
        player.update_resistance(2)  # Passing reduces resistance slightly.
        
        team=game.getTeamWithBall()
        
        if pass_success:
            game.ball=(random.randint(0,5),random.randint(0,1)) #*** Ahora mismo los pases se hacen de forma aleatoria
            game.clock+=1                                             #***pudiendo incluso pasarse a si mismo      
            team.amount_of_passes+=1                                    #!!! Verificar para Cambiar
            
            print("Pase realizado con éxito por jugador " +str(player.id))
            return True
        else:
            game.ball=(0,0)
            team.amount_of_passes=0
            game.possession=not game.possession
            game.clock=0
            print("Pase fallido por jugador " +str(player.id))
            return False
            
            
            

    @staticmethod
    def block_ball(player: Player,game):
        # Blocking effectiveness is influenced by height and jump.
        block_height = player.altura + player.salto_maximo
        block_success = block_height > random.uniform(2.4, 3.0)  # Comparing against an average attack height.

        player.update_resistance(3)  # Blocking is more taxing and reduces resistance more.
        
        if block_success:
            return "Successful block!"
        else:
            return "The block failed to stop the ball."

    @staticmethod
    def shoot_ball(player: Player,game):
        # Shooting/spiking effectiveness is influenced by jump and resistance.
        spike_power = player.salto_maximo * (player.current_resistencia / player.resistencia)
        spike_success = spike_power > random.uniform(0.3, 0.6)

        player.update_resistance(4)  # Spiking is physically demanding and reduces resistance more.
        team=game.getTeamWithBall()
        game.possession=not game.possession
        if spike_success:
            game.ball=(random.randint(0,5),random.randint(0,1)) #*** Ahora mismo los pases se hacen de forma aleatoria
            game.clock+=1                                             #***pudiendo incluso pasarse a si mismo      
            print('Ataque efectivo por parte del Jugador ' + str(player.id)+'!')
            return True
        else:
            game.ball=(0,0)
            game.clock=0
            print('Ataque fallido por parte del Jugador ' + str(player.id)+' :(')
            return False

# Example usage:
# player = Player(altura=1.9, resistencia=100, salto_maximo=0.6, velocidad=5.5)

