from player.player import Player
class FieldTeam:
    def __init__(self, rows, cols,players):
        # Initialize the field as a matrix (2D list) with given dimensions (rows x cols)
        self.field = [[None for _ in range(cols)] for _ in range(rows)]
        self.players = players
        self.currentPlayer=None
        

    def assign_player(self, player_number, area):
        """
        Assign a player to control a specific area in the field.
        :param player_number: The number of the player.
        :param area: A list of tuples indicating the cells (row, col) controlled by the player.
        """
        for (row, col) in area:
            if 0 <= row < len(self.field) and 0 <= col < len(self.field[0]):
                self.field[row][col] = player_number
        self.players[player_number] = area

    def display_field(self):
        """
        Display the field as a matrix with player numbers.
        """
        for row in self.field:
            print(' '.join([str(cell) if cell is not None else '-' for cell in row]))

# Example usage:
# Create a 6x6 field for a team
team_field = FieldTeam(6, 6)

# Assign player 1 to the top-left corner area
team_field.assign_player(1, [(0, 0), (0, 1), (1, 0), (1, 1),(2,0),(0,2),(1,2)])

# Assign player 2 to the top-right corner area
team_field.assign_player(2, [(0, 4), (0, 5), (1, 4), (1, 5),(2,5),(0,3),(1,3)])

# Assign player 3 to the middle area
team_field.assign_player(3, [(2, 2), (2, 3), (3, 2), (3, 3),(2,1),(3,1),(2,4),(3,4)])

team_field.assign_player(4, [(3, 0), (4, 0), (5, 0), (4, 1)])

team_field.assign_player(5, [(5, 1), (4, 2), (4, 3), (5, 2),(5,3),(5,4)])

team_field.assign_player(6, [(5, 5), (4, 5), (3, 5), (4, 4)])
# Display the field
team_field.display_field()