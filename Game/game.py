from field.field import FieldTeam
from field.player.player import Player, Action
import time


class Game:
    #*pienso qe es mejor llevar cada mitad de equipo separado
    team1: FieldTeam
    team2: FieldTeam
    clock: int  #*tiempo transcurrido (pienso qe discreto por eso int)
    score: tuple[int, int]
    possession: bool  #* True: equipo 1 , False: equipo 2

    ball: tuple[int, int]

    def __init__(self, firsTeam: FieldTeam, secondTeam: FieldTeam, time: int, serving: bool):
        self.team1 = firsTeam
        self.team2 = secondTeam
        self.clock = time
        self.possession = serving
        self.ball = (0, 0)
        self.score = (0, 0)

    def Play(self):
        while (self.score[0] < 5 and self.score[1] < 5):
            not_scored = True
            while (not_scored):
                teamWithBall = self.getTeamWithBall()  #Equipo con posesion
                playerWithBall = self.getPlayerWithBall(teamWithBall)  #Jugador con la bola

                actionList = [Action.shoot_ball]  #Lista de acciones posibles
                if (self.clock != 0):
                    actionList.append(Action.pass_ball)

                not_scored = playerWithBall.takeAction(actionList, self)
                if (not not_scored):
                    if (self.possession):
                        self.score = (self.score[0], self.score[1] + 1)
                    else:
                        self.score = (self.score[0] + 1, self.score[1])
                print(not_scored)
                time.sleep(2)
            if (self.possession):
                print("Punto para el equipo 2")
            else:
                print("Punto para el equipo 1")
            print(self.score[0], " ----Equipo 1")
            print(self.score[1], " ----Equipo 2")

        if (self.score[0] == 5):
            print("GANA EQUIPO 1 !!!")
        else:
            print("GANA EQUIPO 2 !!!")

    def getTeamWithBall(self) -> FieldTeam:
        if self.possession:
            return self.team1
        else:
            return self.team2

    def getTheOtherTeam(self) -> FieldTeam:
        if self.possession:
            return self.team2
        else:
            return self.team1

    def getPlayerWithBall(self, team: FieldTeam) -> Player:

        playerNumber = team.field[self.ball[0]][self.ball[1]]
        actualPlayer = team.players[playerNumber]
        return actualPlayer


#* Jugadores para probar     
players = {
    1: Player(1, altura=1.85, resistencia=100, salto_maximo=0.55, velocidad=6.2),
    2: Player(2, altura=1.90, resistencia=95, salto_maximo=0.60, velocidad=6.0),
    3: Player(3, altura=1.78, resistencia=85, salto_maximo=0.52, velocidad=6.5),
    4: Player(4, altura=1.88, resistencia=98, salto_maximo=0.58, velocidad=6.1),
    5: Player(5, altura=1.82, resistencia=90, salto_maximo=0.54, velocidad=6.3),
    6: Player(6, altura=1.92, resistencia=100, salto_maximo=0.62, velocidad=5.9)
}

players2 = {
    11: Player(11, altura=1.85, resistencia=100, salto_maximo=0.55, velocidad=6.2),
    12: Player(12, altura=1.90, resistencia=95, salto_maximo=0.60, velocidad=6.0),
    13: Player(13, altura=1.78, resistencia=85, salto_maximo=0.52, velocidad=6.5),
    14: Player(14, altura=1.88, resistencia=98, salto_maximo=0.58, velocidad=6.1),
    15: Player(15, altura=1.82, resistencia=90, salto_maximo=0.54, velocidad=6.3),
    16: Player(16, altura=1.92, resistencia=100, salto_maximo=0.62, velocidad=5.9)
}
#* Equipos para probar (tienen la misma distribucion en el campo)
#* esto deberia variara segun alguna regla que definamos
# Perform actions
team1 = FieldTeam(6, 6, players)
# Assign player 1 to the top-left corner area
team1.assign_player(1, [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (0, 2), (1, 2)])
# Assign player 2 to the top-right corner area
team1.assign_player(2, [(0, 4), (0, 5), (1, 4), (1, 5), (2, 5), (0, 3), (1, 3)])
# Assign player 3 to the middle area
team1.assign_player(3, [(2, 2), (2, 3), (3, 2), (3, 3), (2, 1), (3, 1), (2, 4), (3, 4)])
team1.assign_player(4, [(3, 0), (4, 0), (5, 0), (4, 1)])
team1.assign_player(5, [(5, 1), (4, 2), (4, 3), (5, 2), (5, 3), (5, 4)])
team1.assign_player(6, [(5, 5), (4, 5), (3, 5), (4, 4)])

team2 = FieldTeam(6, 6, players2)
# Assign player 1 to the top-left corner area
team2.assign_player(11, [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (0, 2), (1, 2)])
# Assign player 2 to the top-right corner area
team2.assign_player(12, [(0, 4), (0, 5), (1, 4), (1, 5), (2, 5), (0, 3), (1, 3)])
# Assign player 3 to the middle area
team2.assign_player(13, [(2, 2), (2, 3), (3, 2), (3, 3), (2, 1), (3, 1), (2, 4), (3, 4)])
team2.assign_player(14, [(3, 0), (4, 0), (5, 0), (4, 1)])
team2.assign_player(15, [(5, 1), (4, 2), (4, 3), (5, 2), (5, 3), (5, 4)])
team2.assign_player(16, [(5, 5), (4, 5), (3, 5), (4, 4)])

match = Game(team1, team2, 0, True)
match.Play()
