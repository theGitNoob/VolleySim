from typing import List

from pandas import DataFrame


class PlayerData:
    def __init__(self, df: DataFrame):
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

        self.roles: List[str] = (
            df["Roles"].split(", ") if "Roles" in df else [self.position]
        )

        self.overall: int = self.calculate_overall()

    def _generate_dorsal(self):
        return abs(hash(f"{self.position}-{self.name}-{self.country}")) % 100

    @staticmethod
    def _set_int_value(value):
        if value != value:
            return 10
        else:
            return int(value)

    def calculate_overall(self) -> int:
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
