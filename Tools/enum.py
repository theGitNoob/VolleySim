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
