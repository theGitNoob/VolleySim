from pandas import DataFrame
from typing import List

class PlayerData():
    def __init__(self, df: DataFrame):
        self.short_name: str = df['short_name']
        self.club_name: str = df['club_name']
        self.club_position: str = df['club_position']
        self.player_positions: List[str] = df['player_positions'].split(', ')
        self.overall: int = self._set_int_value(df['overall'])
        self.pace: int = self._set_int_value(df['pace'])
        self.shooting: int = self._set_int_value(df['shooting'])
        self.passing: int = self._set_int_value(df['passing'])
        self.dribbling: int = self._set_int_value(df['dribbling'])
        self.defending: int = self._set_int_value(df['defending'])
        self.physic: int = self._set_int_value(df['physic'])
        self.attacking_finishing: int = self._set_int_value(df['attacking_finishing'])
        self.mentality_vision: int = self._set_int_value(df['mentality_vision'])
        self.power_stamina: int = self._set_int_value(df['power_stamina']) * 2
        self.mentality_aggression: int = self._set_int_value(df['mentality_aggression'])
        self.mentality_interceptions: int = self._set_int_value(df['mentality_interceptions'])
        self.movement_reactions: int = self._set_int_value(df['movement_reactions'])
        self.dorsal: int = self._set_int_value(df['club_jersey_number'])
        self.goal_keep_diving: int = self._set_int_value(df['goalkeeping_diving'])
        self.goal_keep_reflexes: int = self._set_int_value(df['goalkeeping_reflexes'])
        self.skill_ball_control: int = self._set_int_value(df['skill_ball_control'])

        # Original values
        self.o_short_name: str = df['short_name']
        self.o_club_name: str = df['club_name']
        self.o_club_position: str = df['club_position']
        self.o_player_positions: List[str] = df['player_positions'].split(', ')
        self.o_overall: int = self._set_int_value(df['overall'])
        self.o_pace: int = self._set_int_value(df['pace'])
        self.o_shooting: int = self._set_int_value(df['shooting'])
        self.o_passing: int = self._set_int_value(df['passing'])
        self.o_dribbling: int = self._set_int_value(df['dribbling'])
        self.o_defending: int = self._set_int_value(df['defending'])
        self.o_physic: int = self._set_int_value(df['physic'])
        self.o_attacking_finishing: int = self._set_int_value(df['attacking_finishing'])
        self.o_mentality_vision: int = self._set_int_value(df['mentality_vision'])
        self.o_power_stamina: int = self._set_int_value(df['power_stamina']) * 2
        self.o_mentality_aggression: int = self._set_int_value(df['mentality_aggression'])
        self.o_mentality_interceptions: int = self._set_int_value(df['mentality_interceptions'])
        self.o_movement_reactions: int = self._set_int_value(df['movement_reactions'])
        self.o_dorsal: int = self._set_int_value(df['club_jersey_number'])
        self.o_goal_keep_diving: int = self._set_int_value(df['goalkeeping_diving'])
        self.o_goal_keep_reflexes: int = self._set_int_value(df['goalkeeping_reflexes'])
        self.o_skill_ball_control: int = self._set_int_value(df['skill_ball_control'])

    def _set_int_value(self, value):
        if value != value:
            return 10
        else:
            return value
