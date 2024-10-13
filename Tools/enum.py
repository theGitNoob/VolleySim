from enum import Enum

T1 = "T1"
T2 = "T2"


class PlayerRole(Enum):
    SETTER = "S"  # Colocador
    MIDDLE_BLOCKER = "MB"  # Central
    OUTSIDE_HITTER = "OH"  # Punta o Atacante Exterior
    OPPOSITE_HITTER = "O"  # Opuesto
    LIBERO = "L"  # Líbero
    SUBSTITUTE = "SUB"  # Suplente


# dict_t1 = {
#     1: (1, 1),
#     5: (1, 7),
#     3: (8, 4),
#     4: (7, 7),
#     2: (7, 1),
#     6: (4, 4),
# }
# 
# dict_t2 = {
#     1: (17, 1),
#     2: (17, 7),
#     3: (10, 4),
#     4: (11, 7),
#     5: (11, 1),
#     6: (14, 4),
# }

# positions = {
#     3: LineUpGrid(7, 5, 3, PlayerRole.MIDDLE_BLOCKER),  # Posición 1
#     5: LineUpGrid(1, 6, 5, PlayerRole.OUTSIDE_HITTER),  # Posición 2
#     6: LineUpGrid(4, 4, 6, PlayerRole.LIBERO),  # Posición 3
#     1: LineUpGrid(2, 2, 1, PlayerRole.SETTER),  # Posición 4
#     2: LineUpGrid(6, 2, 2, PlayerRole.OUTSIDE_HITTER),  # Posición 5
#     4: LineUpGrid(5, 7, 4, PlayerRole.OPPOSITE_HITTER),  # Posición 6
# }

dict_t1 = {
    1: (2, 2),
    2: (6, 2),
    3: (7, 5),
    4: (5, 7),
    5: (1, 6),
    6: (4, 4)
}

dict_t2 = {
    1: (17, 2),
    2: (17, 6),
    3: (10, 4),
    4: (11, 7),
    5: (11, 1),
    6: (14, 4)
}
