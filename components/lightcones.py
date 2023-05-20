from dataclasses import dataclass

@dataclass
class Lightcone:
    level: int
    base_hp: int
    base_atk: int
    base_def: int
    percent_hp: float = 0
    percent_atk: float = 0
    percent_def: float = 0
    percent_speed: float = 0
    percent_dmg: float = 0
    crit_rate: float = 0
    crit_dmg: float = 0



the_seriousness_of_breakfast = Lightcone(
    level=80,
    base_hp=846,
    base_atk=476,
    base_def=396,
    percent_dmg=24
)

today_is_another_peaceful_day = Lightcone(
    level=80,
    base_hp=846,
    base_atk=529,
    base_def=330,
    percent_dmg=140*.4  # Hardcoded for QQ
)

before_dawn_s5 = Lightcone(
    level=80,
    base_hp=1058,
    base_atk=582,
    base_def=463,
    crit_dmg=60
)

cruising_in_the_stellar_sea = Lightcone( # S5
    level=80,
    base_hp=952,
    base_atk=529,
    base_def=463,
    crit_rate=16
)

post_op_conversation = Lightcone(
    level=80,
    base_hp=1058,
    base_atk=423,
    base_def=330,
)
