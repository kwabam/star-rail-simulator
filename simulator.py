from characters import Seele
from components.game import Game
from components.lightcones import cruising_in_the_stellar_sea
from components.stats import MainStats, SubStats


def main():
    # Seele Cruising S5 
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