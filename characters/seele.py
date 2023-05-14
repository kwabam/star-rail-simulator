from components.character import Character
from components.game import Game
from components.lightcones import cruising_in_the_stellar_sea
from components.stats import MainStats, SubStats


class Seele(Character):
    def __init__(self, lightcone, main_stats, sub_stats, energy_max=120, ascension=6, level=80):
        super().__init__("seele", lightcone, main_stats, sub_stats, energy_max, ascension, level)

    def act(self):
        if self.game.time >= self.game.time_limit:
            self.game.add_buff(self, "cruising low hp", "crit_rate", 16, 99, 1)

        if self.get_speed() >= 120:
            self.game.add_buff(self, "sss", "percent_atk", 12, 99, 1)

        damage = 0
        if self.energy >= self.energy_max:  # ult at start of turn. This gives extra turn of buff.
            damage += self.ult()
        if self.game.skill_points > 0:
            damage += self.skill()
        else:
            damage += self.basic()

        self.game.add_damage(damage)

    def basic(self):
        dmg = self.calculate_base_dmg(mv=1)
        self.game.skill_points += 1
        self.add_energy(20)
        print("basic damage: ", dmg)
        return dmg

    def skill(self):
        self.game.add_buff(self, "skill_speed", "percent_speed", 25, 2)
        self.game.skill_points -= 1
        self.add_energy(30)
        dmg = self.calculate_base_dmg(mv=2.20)
        print("skill damage: ", dmg)
        return dmg

    def ult(self):
        # only ults at start so
        # buff effectively lasts 2 turns
        self.game.add_buff(self, "talent_dmg", "percent_dmg", 80, 2)
        self.game.add_buff(self, "talent_pen", "percent_penetration", 20, 2)
        self.energy = 5
        dmg = self.calculate_base_dmg(mv=4.25)
        print("ult damage: ", dmg)
        return dmg


def main():
    main_stats = MainStats(flat_hp=1, flat_atk=1, crit_rate=1, percent_atk=2, percent_dmg=1)
    sub_stats = SubStats(flat_speed=1, percent_atk=3, crit_rate=10, crit_dmg=10)
    seele = Seele(cruising_in_the_stellar_sea, main_stats, sub_stats)
    seele.percent_atk += 12  # SSS
    seele.percent_def_ignore = 10  # quantum set
    seele.percent_dmg += 10  # quantum set

    game = Game(team=[seele], skill_points=20)
    seele.game = game
    # seele uses technique before entering battle
    game.add_buff(seele, "talent_dmg", "percent_dmg", 80, 1)
    game.add_buff(seele, "talent_pen", "percent_penetration", 20, 1)

    game.play()


if __name__ == "__main__":
    main()
