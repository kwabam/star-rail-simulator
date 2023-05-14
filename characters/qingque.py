import random
import matplotlib.pyplot as plt
import numpy as np

from components.character import Character
from components.lightcones import the_seriousness_of_breakfast
from components.stats import MainStats, SubStats


class Qingque(Character):
    def __init__(self, lightcone, main_stats, sub_stats, energy_max=140, ascension=6, level=80):
        super().__init__("qingque", lightcone, main_stats, sub_stats, energy_max, ascension, level)

    def act(self): # TODO: Refactor this whole class to use game logic
        pass

    def basic(self):
        pass

    def skill(self):
        pass

    def ult(self):
        pass

def remove_suit(hand, suit):
    if suit in hand:
        hand.remove(suit)
    return hand


# https://colab.research.google.com/drive/1lKI9ziUxsovuDVzfTXioQAjEjPt9qv8p
def process_suit_removal(hand, counts, primary, secondary, tertiary):
    # primary is a suit that we have >= 2 of
    # we have 5 tiles in hand
    # secondary/tertiary not ordered by count

    # if there is no tiles of secondary suit
    if counts.get(secondary, 0) == 0:
        # remove the least common suit
        if counts[primary] > counts[tertiary]:
            return remove_suit(hand, tertiary)
        else:
            return remove_suit(hand, primary)
    # if there is no tiles of tertiary suit
    elif counts.get(tertiary, 0) == 0:
        # remove the least common suit
        if counts[primary] > counts[secondary]:
            return remove_suit(hand, secondary)
        else:
            return remove_suit(hand, primary)
    # if there are  tiles of all suits
    if counts[secondary] >= 1 and counts[tertiary] >= 1:
        # if secondary > tertiary, then we have 2 pairs. remove single.
        if counts[secondary] > counts[tertiary]:
            return remove_suit(hand, tertiary)
        # same as above, but vice versa
        elif counts[tertiary] > counts[secondary]:
            return remove_suit(hand, secondary)
        # if secondary == tertiary, then remove random one between them (we have 3 primary, 1 secondary, 1 tertiary)
        elif random.random() < 0.5:
            return remove_suit(hand, secondary)
        else:
            return remove_suit(hand, tertiary)


def draw_tile(hand):
    suits = ['Wan', 'Tong', 'Tiao']
    # if <4 tiles in hand, draw a random tile
    if len(hand) < 4:
        hand.append(random.choice(suits))
        return hand
    # if 4 of a kind, no changes
    if check_four_of_a_kind(hand):
        return hand

    # draw a random tile
    hand.append(random.choice(suits))
    counts = count_tiles(hand)

    # hand size is 5
    # at least one of the suits has a pair
    # run algorithm to determine which tile to remove
    if counts.get('Wan', 0) >= 2 and len(hand) == 5:
        process_suit_removal(hand, counts, 'Wan', 'Tong', 'Tiao')
    if counts.get('Tong', 0) >= 2 and len(hand) == 5:
        process_suit_removal(hand, counts, 'Tong', 'Wan', 'Tiao')
    if counts.get('Tiao', 0) >= 2 and len(hand) == 5:
        process_suit_removal(hand, counts, 'Tiao', 'Wan', 'Tong')

    return hand


def draw_tiles(hand, num_tiles=2):
    for _ in range(num_tiles):
        hand = draw_tile(hand)
    return hand


def count_tiles(tiles):
    counts = {'Wan': 0, 'Tong': 0, 'Tiao': 0}
    for tile in tiles:
        counts[tile] += 1
    return counts


def check_four_of_a_kind(hand):
    tile_counts = count_tiles(hand)
    return any(count >= 4 for count in tile_counts.values())


def qing_que_simulation(character, max_time=850):
    outcomes = {
        "skills": [0, 0, 0, 0, 0, 0, 0],
        "hits": 0,
        "ults": 0,
        "autarky": 0,
        "whiff_ults": 0,
        "whiffs": 0,
    }


    enemy_level = 80
    enemy_def = 200 + 10 * enemy_level
    enemy_def = .8 * enemy_def  # quantum set
    toughness_multiplier = .9  # unbroken enemies take 10% less damage
    def_multiplier = 1 - (enemy_def / (enemy_def + 200 + 10 * character.level))

    max_skills = 6  # maximum skills allowed to use per turn
    ult_skill_threshold = 0  # do not ult unless at least this amount of skills has been used, unless whiffed on draws

    total_dmg = 0

    qq_basic1_mv = 1.1
    qq_basic2_mv = 2.64

    qq_ult_mv = 2.16
    speed_buff = 0

    trace2 = True

    skill_points = 3

    hand = []

    time = 10000 / character.get_speed()
    while time < max_time:
        for i in range(4):  # draw 1 tile for each teammate and 1 for self
            hand = draw_tile(hand)
            character.energy += 1
            if skill_points < 5 and i != 3:  # qq doesnt gen skill point at start
                skill_points += 1
            if check_four_of_a_kind(hand):
                break
        print(f"Time: {time:.2f}, Skill Points: {skill_points}, Energy: {character.energy}, Damage: {total_dmg:.2f}")

        if trace2:
            skill_points += 1  # trace 2 gives 1 free skill at start of battle
            trace2 = False

        dmg_percent_buff = 0  # dmg percent buff from talent and a4 trace
        autarky = False  # whether e4 has activated this round
        skills_used = 0  # number of skills used this round

        while skill_points > 0 and not check_four_of_a_kind(hand) and skills_used < max_skills:
            # Use skill
            hand = draw_tiles(hand, 2)
            skill_points -= 1
            skills_used += 1
            character.energy += 1
            if skills_used < 4:  # can only get up to 4 buffs from skill
                dmg_percent_buff += (31 + 10)
            if not autarky and random.random() < .24:  # 1st condition avoids dupe prints
                print("autarky")
                outcomes["autarky"] += 1
                autarky = True  # e4: 24% fixed chance for autarky, which doubles basic attack damage

        print("skills: ", skills_used)
        outcomes["skills"][skills_used] += 1
        if check_four_of_a_kind(hand):  # 4 of a kind
            print("4 of a kind")
            outcomes["hits"] += 1
            hand = []  # discard hand
            atk_percent_buff = 79  # enter hidden hand state
            if skill_points < 5:
                skill_points += 1
            speed_buff = 10  # A6 trace
            base_dmg = 0
            if skills_used >= ult_skill_threshold and character.energy > character.energy_max:  # ult
                print("ult")
                outcomes["ults"] += 1
                base_dmg += character.calculate_base_dmg(qq_ult_mv,
                                                         dmg_percent_buff=dmg_percent_buff + 10,
                                                         atk_percent_buff=atk_percent_buff)
                character.energy = 5
            # auto
            base_dmg += (2 if autarky else 1) * character.calculate_base_dmg(qq_basic2_mv,
                                                                             dmg_percent_buff=dmg_percent_buff,
                                                                             atk_percent_buff=atk_percent_buff)
            outgoing_dmg = base_dmg * toughness_multiplier * def_multiplier
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        else:  # whiff
            base_dmg = 0
            if character.energy > character.energy_max:  # ult, gets you to 4 of a kind
                print("ult")
                outcomes["whiff_ults"] += 1
                base_dmg += character.calculate_base_dmg(qq_ult_mv, dmg_percent_buff=dmg_percent_buff + 10)
                hand = []  # discard hand
                atk_percent_buff = 79  # enter hidden hand state
                skill_points += 1
                character.energy = 5
                base_dmg += (2 if autarky else 1) * character.calculate_base_dmg(qq_basic2_mv,
                                                                                 dmg_percent_buff=dmg_percent_buff,
                                                                                 atk_percent_buff=atk_percent_buff)
            else:
                print("whiff")
                outcomes["whiffs"] += 1
                base_dmg += (2 if autarky else 1) * character.calculate_base_dmg(qq_basic1_mv,
                                                                                 dmg_percent_buff=dmg_percent_buff)
                # discard least common tile
                counts = count_tiles(hand)
                least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
                hand.remove(least_common_suit)

            outgoing_dmg = base_dmg * toughness_multiplier * def_multiplier
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        character.energy += 20
        av = 10000 / character.get_speed(percent_buff=speed_buff)
        speed_buff = 0
        time += av
    print("Total damage: ", total_dmg)
    print("Outcomes: ", outcomes)
    return total_dmg, outcomes


def run_simulation(num_simulations=10000):
    results = []
    outcomes_dict = {
        "skills": [0, 0, 0, 0, 0, 0, 0],
        "hits": 0,
        "ults": 0,
        "autarky": 0,
        "whiff_ults": 0,
        "whiffs": 0,
    }
    main_stats = MainStats(flat_hp=1, flat_atk=1, flat_speed=1, crit_rate=1, percent_atk=1, percent_dmg=1)
    sub_stats = SubStats(percent_atk=4, crit_rate=10, crit_dmg=10)
    qq = Qingque(the_seriousness_of_breakfast,  main_stats, sub_stats, energy_max=140)
    qq.percent_atk += 24 # SSS
    qq.percent_dmg += 10 # quantum set

    for i in range(num_simulations):
        print(f"Simulation {i + 1}")
        dmg, outcomes = qing_que_simulation(qq)
        results.append(dmg)

        for key in outcomes_dict:
            if key == "skills":
                for i in range(len(outcomes[key])):
                    outcomes_dict[key][i] += outcomes[key][i]
            else:
                outcomes_dict[key] += outcomes[key]
        print("--------------------------------------------------------------------------\n")

    # Calculate average damage and display it
    average_dmg = sum(results) / num_simulations
    print(f"Average damage: {average_dmg:.2f}")
    first_quartile = np.percentile(results, 25)
    third_quartile = np.percentile(results, 75)

    print(f"25th percentile (first quartile): {first_quartile:.2f}")
    print(f"75th percentile (third quartile): {third_quartile:.2f}")

    # Calculate and display average outcomes
    print("Average outcomes:")
    average_turns = sum(outcomes_dict["skills"]) / num_simulations
    for key in outcomes_dict:
        if key == "skills":
            print("Skills:")
            average_skills_used = 0
            for i in range(len(outcomes_dict[key])):
                avg = outcomes_dict[key][i] / num_simulations
                print(f"{i}: {avg:.2f}", end=" | ")
                average_skills_used += avg * i

            print(f"\nAverage skills used per turn: {average_skills_used / average_turns:.2f}")

        else:
            avg = outcomes_dict[key] / num_simulations
            if key in ["hits", "autarky", "whiff_ults", "whiffs"]:
                print(f"{key}: {100 * avg / average_turns:.2f}%")
            else:
                print(f"{key}: {avg:.2f}")
    print(f"Average turns: {average_turns:.2f}")

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
