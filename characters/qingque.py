import random
import matplotlib.pyplot as plt
import numpy as np

from components import Game
from components.character import Character
from components.lightcones import the_seriousness_of_breakfast
from components.stats import MainStats, SubStats


class Qingque(Character):  # e6
    def __init__(self, lightcone, main_stats, sub_stats, energy_max=140, ascension=6, level=80):
        super().__init__("qingque", lightcone, main_stats, sub_stats, energy_max, ascension, level)
        self.trace2 = True
        self.hand = []
        self.autarky = False

    def draw_tile(self):
        # this method is super long because this is how the game implements it
        suits = ['Wan', 'Tong', 'Tiao']
        # if <4 tiles in hand, draw a random tile
        if len(self.hand) < 4:
            self.hand.append(random.choice(suits))
            self.add_energy(1)
            return
        # if 4 of a kind, no changes
        if self.has_four_of_a_kind():
            return

        # draw a random tile
        self.hand.append(random.choice(suits))
        counts = self.count_tiles()

        # hand size is 5
        # at least one of the suits has a pair
        # run algorithm to determine which tile to remove
        if counts.get('Wan', 0) >= 2 and len(self.hand) == 5:
            self.process_suit_removal(counts, 'Wan', 'Tong', 'Tiao')
        if counts.get('Tong', 0) >= 2 and len(self.hand) == 5:
            self.process_suit_removal(counts, 'Tong', 'Wan', 'Tiao')
        if counts.get('Tiao', 0) >= 2 and len(self.hand) == 5:
            self.process_suit_removal(counts, 'Tiao', 'Wan', 'Tong')

    def remove_suit(self, suit):
        if suit in self.hand:
            self.hand.remove(suit)

    # https://colab.research.google.com/drive/1lKI9ziUxsovuDVzfTXioQAjEjPt9qv8p
    def process_suit_removal(self, counts, primary, secondary, tertiary):
        # primary is a suit that we have >= 2 of
        # we have 5 tiles in hand
        # secondary/tertiary not ordered by count

        # if there is no tiles of secondary suit
        if counts.get(secondary, 0) == 0:
            # remove the least common suit
            if counts[primary] > counts[tertiary]:
                return self.remove_suit(tertiary)
            else:
                return self.remove_suit(primary)
        # if there is no tiles of tertiary suit
        elif counts.get(tertiary, 0) == 0:
            # remove the least common suit
            if counts[primary] > counts[secondary]:
                return self.remove_suit(secondary)
            else:
                return self.remove_suit(primary)
        # if there are  tiles of all suits
        if counts[secondary] >= 1 and counts[tertiary] >= 1:
            # if secondary > tertiary, then we have 2 pairs. remove single.
            if counts[secondary] > counts[tertiary]:
                return self.remove_suit(tertiary)
            # same as above, but vice versa
            elif counts[tertiary] > counts[secondary]:
                return self.remove_suit(secondary)
            # if secondary == tertiary, then remove random one between them (we have 3 primary, 1 secondary, 1 tertiary)
            elif random.random() < 0.5:
                return self.remove_suit(secondary)
            else:
                return self.remove_suit(tertiary)

    def draw_tiles(self, num_tiles=2):
        for _ in range(num_tiles):
            self.draw_tile()

    def count_tiles(self):
        counts = {'Wan': 0, 'Tong': 0, 'Tiao': 0}
        for tile in self.hand:
            counts[tile] += 1
        return counts

    def has_four_of_a_kind(self):
        tile_counts = self.count_tiles()
        return any(count >= 4 for count in tile_counts.values())

    def act(self):
        for i in range(3): # simulate drawing for teammates
            self.draw_tile()  # obviously not ideal, full team sim will need to force game to check for qq... will be awkward
            self.game.add_skill_point()
        self.draw_tile()
        while self.game.skill_points > 0 and not self.has_four_of_a_kind():
            if self.trace2:
                self.game.skill_points += 1  # first skill is free
                self.trace2 = False
            self.skill()
        if self.has_four_of_a_kind():
            self.game.add_buff(self, buff_name="hidden hand", buff_type="percent_atk", buff_value=79, duration=1)
            if self.energy >= self.energy_max:
                self.ult()
            self.basic2()
        else:
            if self.energy >= self.energy_max:
                self.ult()
                self.basic2()
            else:
                self.basic()
        self.autarky = False

    def basic(self):
        dmg = 0
        self.add_energy(20)
        counts = self.count_tiles()
        least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
        self.hand.remove(least_common_suit)
        dmg += (2 if self.autarky else 1) * self.calculate_base_dmg(1.1)
        self.game.add_damage(dmg)

    def basic2(self):  # 4 of a kind
        dmg = 0
        self.add_energy(20)
        self.game.add_buff(self, buff_name="qq a6 trace", buff_type="percent_speed", buff_value=10, duration=1)
        self.hand = []  # discard hand
        self.game.add_skill_point()
        dmg += (2 if self.autarky else 1) * self.calculate_base_dmg(2.64)
        self.game.add_damage(dmg)

    def skill(self):
        self.draw_tiles(2)
        self.energy += 2
        self.game.skill_points -= 1
        self.game.add_buff(self, buff_name="qq skill", buff_type="percent_dmg", buff_value=41, duration=1, max_instances=4)
        if not self.autarky and random.random() < .24:
            self.autarky = True  # e4: 24% fixed chance for autarky, which doubles basic attack damage

    def ult(self):
        self.energy = 5
        dmg = self.calculate_base_dmg(2.16, dmg_percent_buff=10)
        self.hand = ['Wan', 'Wan', 'Wan', 'Wan']  # set hand to 4 of a kind
        self.game.add_buff(self, buff_name="hidden hand", buff_type="percent_atk", buff_value=79, duration=1)
        self.game.add_damage(dmg)


def run_simulation(num_simulations=10000):
    results = []
    # outcomes_dict = {
    #     "skills": [0, 0, 0, 0, 0, 0, 0],
    #     "hits": 0,
    #     "ults": 0,
    #     "autarky": 0,
    #     "whiff_ults": 0,
    #     "whiffs": 0,
    # }
    main_stats = MainStats(flat_hp=1, flat_atk=1, flat_speed=1, crit_rate=1, percent_atk=1, percent_dmg=1)
    sub_stats = SubStats(percent_atk=4, crit_rate=10, crit_dmg=10)
    qq = Qingque(the_seriousness_of_breakfast, main_stats, sub_stats, energy_max=140)
    qq.percent_atk += 24  # SSS
    qq.percent_dmg += 10  # quantum set
    qq.percent_def_ignore += 10  # quantum set

    for i in range(num_simulations):
        print(f"Simulation {i + 1}")
        game = Game(team=[qq])
        game.play()
        #dmg, outcomes = qing_que_simulation(qq)
        results.append(game.total_damage)

        # for key in outcomes_dict:
        #     if key == "skills":
        #         for i in range(len(outcomes[key])):
        #             outcomes_dict[key][i] += outcomes[key][i]
        #     else:
        #         outcomes_dict[key] += outcomes[key]
        # print("--------------------------------------------------------------------------\n")

    # Calculate average damage and display it
    average_dmg = sum(results) / num_simulations
    print(f"Average damage: {average_dmg:.2f}")
    first_quartile = np.percentile(results, 25)
    third_quartile = np.percentile(results, 75)

    print(f"25th percentile (first quartile): {first_quartile:.2f}")
    print(f"75th percentile (third quartile): {third_quartile:.2f}")

    # Calculate and display average outcomes
    # print("Average outcomes:")
    # average_turns = sum(outcomes_dict["skills"]) / num_simulations
    # for key in outcomes_dict:
    #     if key == "skills":
    #         print("Skills:")
    #         average_skills_used = 0
    #         for i in range(len(outcomes_dict[key])):
    #             avg = outcomes_dict[key][i] / num_simulations
    #             print(f"{i}: {avg:.2f}", end=" | ")
    #             average_skills_used += avg * i
    #
    #         print(f"\nAverage skills used per turn: {average_skills_used / average_turns:.2f}")
    #
    #     else:
    #         avg = outcomes_dict[key] / num_simulations
    #         if key in ["hits", "autarky", "whiff_ults", "whiffs"]:
    #             print(f"{key}: {100 * avg / average_turns:.2f}%")
    #         else:
    #             print(f"{key}: {avg:.2f}")
    # print(f"Average turns: {average_turns:.2f}")

    # Display damage distribution using a histogram
    plt.hist(results, bins='auto', edgecolor='black')
    plt.xlabel('Damage')
    plt.ylabel('Frequency')
    plt.title('Damage Distribution')

    # Add average, 25th, and 75th percentiles, lowest, and highest numbers to the chart
    ymin, ymax = plt.ylim()
    plt.axvline(average_dmg, color='r', linestyle='dashed', linewidth=2)
    plt.text(average_dmg, ymax * 0.95, f'Average: {average_dmg:.0f}', rotation=0, color='r')

    plt.axvline(first_quartile, color='g', linestyle='dashed', linewidth=2)
    plt.axvline(third_quartile, color='b', linestyle='dashed', linewidth=2)

    plt.show()


if __name__ == "__main__":
    run_simulation(10000)
