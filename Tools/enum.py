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


dict_t1 = {
    1: (1, 1),
    5: (1, 7),
    3: (8, 4),
    4: (7, 7),
    2: (7, 1),
    6: (4, 4),
}

dict_t2 = {
    1: (17, 1),
    2: (17, 7),
    3: (10, 4),
    4: (11, 7),
    5: (11, 1),
    6: (14, 4),
}
