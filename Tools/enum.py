from enum import Enum

T1 = "T1"
T2 = "T2"


class PlayerRole(Enum):
    SETTER = "S"
    MIDDLE_BLOCKER = "MB"
    OUTSIDE_HITTER = "OH"
    OPPOSITE_HITTER = "O"
    LIBERO = "L"


dict_t1 = {1: (2, 2), 2: (6, 2), 3: (7, 5), 4: (5, 7), 5: (1, 6), 6: (4, 4)}

dict_t2 = {1: (17, 6), 2: (11, 7), 3: (10, 4), 4: (11, 1), 5: (17, 2), 6: (14, 4)}
