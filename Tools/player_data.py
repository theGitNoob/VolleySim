from typing import List

from pandas import DataFrame


class PlayerData:
    def __init__(self, df: DataFrame):
        # Atributos principales
        self.name: str = df["Name"]
        self.position: str = df["Position"]
        self.p_attack: int = self._set_int_value(df["p_Attack"])
        self.p_block: int = self._set_int_value(df["p_Block"])
        self.p_dig: int = self._set_int_value(df["p_Dig"])
        self.p_set: int = self._set_int_value(df["p_Set"])
        self.p_serve: int = self._set_int_value(df["p_Serve"])
        self.p_receive: int = self._set_int_value(df["p_Receive"])
        self.country: str = df["Team"]
        self.errors: int = 0
        self.dorsal: int = (
            self._set_int_value(df["Dorsal"])
            if "Dorsal" in df
            else self._generate_dorsal()
        )

        # Roles que puede desempeñar el jugador (si aplica)
        self.roles: List[str] = (
            df["Roles"].split(", ") if "Roles" in df else [self.position]
        )

        # Calificación general del jugador
        self.overall: int = self.calculate_overall()

    # Generar dorsal de tal forma que no existan 2 jugadores con el mismo dorsal aunque no sean del mismo equipo
    def _generate_dorsal(self):
        return abs(hash(f"{self.position}-{self.name}-{self.country}")) % 100

    @staticmethod
    def _set_int_value(value):
        if value != value:  # Verifica si el valor es NaN
            return 10  # Valor por defecto si es NaN
        else:
            return int(value)

    def calculate_overall(self) -> int:
        """
        Calcula una calificación general (overall) del jugador
        basado en sus habilidades principales.
        """
        attributes = [
            self.p_attack,
            self.p_block,
            self.p_dig,
            self.p_set,
            self.p_serve,
            self.p_receive,
        ]
        return int(sum(attributes) / len(attributes))

    def repr(self):
        return f"PlayerData(name={self.name}, position={self.position}, overall={self.overall})"
