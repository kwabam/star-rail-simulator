from random import random

from components import *


class Natasha(Character):  # e6
    def __init__(self, lightcone, main_stats, sub_stats, energy_max=90, ascension=6, level=80):
        super().__init__("natasha", lightcone, main_stats, sub_stats, energy_max, ascension, level)

    # override since natashas damage also uses hp as MV
    def calculate_base_dmg(self, mv, atk_percent_buff=0, dmg_percent_buff=0, crit_rate_buff=0, crit_dmg_buff=0):
        if self.random_crits: # simulate crits and non crits
            if random.random() < self.get_crit_rate(crit_rate_buff=crit_rate_buff):  # if you crit
                mv *= self.get_crit_damage_multiplier(crit_dmg_buff=crit_dmg_buff)  # multiply by crit damage multiplier
        else:
            mv *= self.get_average_crit_multiplier() # just multiply by average crit multiplier
        return mv \
            * (self.get_atk(percent_buff=atk_percent_buff) + .4 * self.get_hp()) \
            * self.get_dmg_multiplier(dmg_percent_buff=dmg_percent_buff)

    def act(self):
        self.game.add_damage(self.basic())

    def basic(self):
        dmg = self.calculate_base_dmg(mv=1)
        self.game.add_skill_point()
        print(f"basic dmg: {dmg}")
        return dmg

    def skill(self):
        pass

    def ult(self):
        pass


def simulate():
    main_stats = MainStats(flat_hp=1, flat_atk=1, percent_hp=2, flat_speed=1, percent_heal=1)
    sub_stats = SubStats(flat_speed=10, percent_hp=10)
    natasha = Natasha(post_op_conversation, main_stats, sub_stats)
    natasha.percent_hp += 12  # fleet of the ageless
    natasha.percent_dmg += 10  # musketeer, only autos damage
    natasha.percent_speed += 6  # musketeer

    game = Game(team=[natasha], skill_points=20)
    game.add_aoe_buff("natasha_fleet", "percent_atk", 8, 99, 1)
    game.play()


if __name__ == '__main__':
    simulate()
