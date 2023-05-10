from dataclasses import dataclass, fields
import random
from typing import Optional
from lightcones import Lightcone

@dataclass
class Character:
    level: int
    base_hp: int
    base_atk: int
    base_def: int
    base_speed: int
    lightcone: Lightcone
    energy_max: int
    flat_hp: Optional[float] = 0
    flat_atk: Optional[float] = 0
    flat_def: Optional[float] = 0
    flat_speed: Optional[float] = 0
    percent_hp: Optional[float] = 0
    percent_atk: Optional[float] = 0
    percent_def: Optional[float] = 0
    percent_speed: Optional[float] = 0
    percent_dmg: Optional[float] = 0
    crit_rate: Optional[float] = 5
    crit_dmg: Optional[float] = 50

    def __post_init__(self):
        self.energy = self.energy_max / 2
        fields_to_add = [field.name for field in fields(self.lightcone) if field.name != 'level']
        for field in fields_to_add:
            base_field_value = getattr(self, field)
            lightcone_field_value = getattr(self.lightcone, field, 0)
            setattr(self, field, base_field_value + lightcone_field_value)


    def get_hp(self):
        return self.base_hp * (1 + self.percent_hp) + self.flat_hp

    def get_atk(self, flat_buff=0, percent_buff=0):
        return self.base_atk * (100 + self.percent_atk + percent_buff) / 100 + self.flat_atk + flat_buff

    def get_def(self, flat_buff=0, percent_buff=0):
        return self.base_def * (100 + self.percent_def + percent_buff) / 100 + self.flat_def + flat_buff

    def get_speed(self, flat_buff=0, percent_buff=0):
        return self.base_speed * (100 + self.percent_speed + percent_buff) / 100 + self.flat_speed + flat_buff

    def get_average_crit_multiplier(self, crit_rate_buff=0, crit_dmg_buff=0):
        return 1 + (self.crit_rate / 100 * self.crit_dmg / 100)

    def get_crit_rate(self, crit_rate_buff=0):
        return (self.crit_rate + crit_rate_buff) / 100

    def get_crit_damage_multiplier(self, crit_dmg_buff=0):
        return 1 + ((self.crit_dmg + crit_dmg_buff) / 100)

    def get_dmg_multiplier(self, dmg_percent_buff=0):
        return (100 + self.percent_dmg + dmg_percent_buff) / 100

    def calculate_base_dmg(self, mv, atk_percent_buff=0, dmg_percent_buff=0, crit_rate_buff=0, crit_dmg_buff=0):
        if random.random() < self.get_crit_rate(crit_rate_buff=crit_rate_buff):  # if you crit
            mv *= self.get_crit_damage_multiplier(crit_dmg_buff=crit_dmg_buff)  # multiply by crit damage multiplier
        return mv \
               * self.get_atk(percent_buff=atk_percent_buff) \
               * self.get_dmg_multiplier(dmg_percent_buff=dmg_percent_buff)
