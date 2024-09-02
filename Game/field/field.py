class FieldTeam:
    def __init__(self, rows, cols, players):
        # Initialize the field as a matrix (2D list) with given dimensions (rows x cols)
        self.field = [[None for _ in range(cols)] for _ in range(rows)]
        self.players = players
        self.currentPlayer = None
        self.amount_of_passes = 0

    def assign_player(self, player_number, area):
        """
        Assign a player to control a specific area in the field.
        :param player_number: The number of the player.
        :param area: A list of tuples indicating the cells (row, col) controlled by the player.
        """
        for (row, col) in area:
            if 0 <= row < len(self.field) and 0 <= col < len(self.field[0]):
                self.field[row][col] = player_number
        

    def display_field(self):
        """
        Display the field as a matrix with player numbers.
        """
        for row in self.field:
            print(' '.join([str(cell) if cell is not None else '-' for cell in row]))

# Example usage:
# Create a 6x6 field for a team
