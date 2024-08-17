from field.field import FieldTeam
from field.player.player import Player
class Game:
    #*pienso qe es mejor llevar cada mitad de equipo separado
    team1:FieldTeam 
    team2:FieldTeam
    clock:int #*tiempo transcurrido (pienso qe discreto por eso int)
    score:tuple[int,int]
    servingTeam:bool #* True: equipo 1 , False: equipo 2
    ball:tuple[int,int]
    def __init__(self,firsTeam:FieldTeam,secondTeam:FieldTeam,time:int,serving:bool):
        self.team1=firsTeam
        self.team2=secondTeam
        self.clock=time
        self.servingTeam=serving 
    def start():
     #* Jugadores para probar     
# players={'1' : Player(altura=1.85, resistencia=100, salto_maximo=0.55, velocidad=6.2),
# "2" : Player(altura=1.90, resistencia=95, salto_maximo=0.60, velocidad=6.0),
# "3" : Player(altura=1.78, resistencia=85, salto_maximo=0.52, velocidad=6.5),
# "4" : Player(altura=1.88, resistencia=98, salto_maximo=0.58, velocidad=6.1),
# "5" : Player(altura=1.82, resistencia=90, salto_maximo=0.54, velocidad=6.3),
# "6" : Player(altura=1.92, resistencia=100, salto_maximo=0.62, velocidad=5.9)
# }
    