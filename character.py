class Lightcone:
    def __init__(self, level, hp, atk, defense):
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defense = defense


class Character:
    def __init__(self, level, base_hp, base_atk, base_def, base_speed, lightcone, energy_max,
                 flat_hp=0, flat_atk=0, flat_def=0, flat_speed=0,
                 percent_hp=0, percent_atk=0, percent_def=0, percent_speed=0,
                 crit_rate=5, crit_dmg=50, dmg_percent=0):
        self.level = level
        self.base_hp = base_hp + lightcone.hp
        self.base_atk = base_atk + lightcone.atk
        self.base_def = base_def + lightcone.defense
        self.base_speed = base_speed
        self.energy = energy_max/2
        self.energy_max = energy_max
        self.flat_hp = flat_hp
        self.flat_atk = flat_atk
        self.flat_def = flat_def
        self.flat_speed = flat_speed
        self.percent_hp = percent_hp
        self.percent_atk = percent_atk
        self.percent_def = percent_def
        self.percent_speed = percent_speed
        self.crit_rate = crit_rate
        self.crit_dmg = crit_dmg
        self.dmg_percent = dmg_percent

    def get_hp(self):
        return self.base_hp * (1 + self.percent_hp) + self.flat_hp

    def get_atk(self, flat_buff=0, percent_buff=0):

        return self.base_atk * (100 + self.percent_atk + percent_buff) / 100 + self.flat_atk + flat_buff

    def get_def(self, flat_buff=0, percent_buff=0):
        return self.base_def * (100 + self.percent_def + percent_buff) / 100 + self.flat_def + flat_buff

    def get_speed(self, flat_buff=0, percent_buff=0):
        return self.base_speed * (100 + self.percent_speed + percent_buff) / 100 + self.flat_speed + flat_buff

    def get_crit_multiplier(self, crit_rate_buff=0, crit_dmg_buff=0):
        return 1 + (self.crit_rate/100 * self.crit_dmg/100)

    def get_dmg_multiplier(self, dmg_percent_buff=0):
        return (100 + self.dmg_percent + dmg_percent_buff) / 100

    def calculate_base_dmg(self, mv, atk_percent_buff=0, dmg_percent_buff=0):
        return mv \
               * self.get_atk(percent_buff=atk_percent_buff) \
               * self.get_dmg_multiplier(dmg_percent_buff=dmg_percent_buff) \
               * self.get_crit_multiplier()

