import random
import matplotlib.pyplot as plt
import numpy as np
from character import Character, Lightcone
import builtins
from contextlib import contextmanager


@contextmanager
def disable_print():
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: None
    try:
        yield
    finally:
        builtins.print = original_print


def draw_tile():
    return random.choice(['A', 'B', 'C'])


def draw_tiles(num_tiles):
    return [draw_tile() for _ in range(num_tiles)]


def count_tiles(tiles):
    counts = {'A': 0, 'B': 0, 'C': 0}
    for tile in tiles:
        counts[tile] += 1
    return counts


def check_four_of_a_kind(tile_counts):
    return any(count >= 4 for count in tile_counts.values())


def update_hand(hand, new_tiles):
    hand.extend(new_tiles)
    counts = count_tiles(hand)

    while len(hand) > 4:
        least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
        hand.remove(least_common_suit)
        counts[least_common_suit] -= 1

    return hand


def qing_que_simulation(max_time=850):
    outcomes = {
        "skills": [0, 0, 0, 0, 0, 0, 0],
        "hits": 0,
        "ults": 0,
        "whiff_ults": 0,
        "whiffs": 0,
    }

    the_seriousness_of_breakfast = Lightcone(
        level=80,
        hp=846,
        atk=476,
        defense=396
    )

    today_is_another_peaceful_day = Lightcone(
        level=80,
        hp=846,
        atk=529,
        defense=330
    )

    qing_que = Character(
        level=80,
        base_hp=1023,
        base_atk=652,
        base_def=441,
        base_speed=98,
        flat_hp=705,
        flat_atk=(56.4479991140058 + 19.7567996907402 * 15),  # main stat (gloves)
        flat_speed=25,
        percent_atk=(6.91199985661483 + 2.41920001267946 * 15)  # main stat
                    + (3.4559999981566 + 0.431999999769576) * 4  # substats
                    + 24  # planetary set bonus
                    + 28,  # traces
        percent_def=12.5,  # traces
        crit_rate=5 + (5.18399999723491 + 1.8143999571227 * 15)  # main stat
                  + (2.59199999861745 + 0.32400001728948) * 10,  # substats
        crit_dmg=50 + (5.18399999723491 + 0.64800003457896) * 10,  # substats
        dmg_percent=(6.22079991286286 + 2.17730006045792 * 15)  # main stat
                    + 10 + 14.4  # traces
                    + .4 * 140,  # today is another peaceful day
        lightcone=today_is_another_peaceful_day,
        energy_max=140
    )

    enemy_level = 80
    enemy_def = 200 + 10 * enemy_level
    enemy_def = .8 * enemy_def  # quantum set
    toughness_multiplier = .9 # unbroken enemies take 10% less damage
    def_multiplier = 1 - (enemy_def / (enemy_def + 200 + 10 * qing_que.level))

    total_dmg = 0

    qq_basic1_mv = 1.1
    qq_basic2_mv = 2.64

    qq_ult_mv = 2.16
    speed_buff = 0

    trace2 = True

    skill_points = 3

    tiles = []

    time = 10000 / qing_que.get_speed()
    while time < max_time:
        for i in range(4):  # draw 1 tile for each teammate and 1 for self
            tiles = update_hand(tiles, draw_tiles(1))
            qing_que.energy += 1
            if skill_points < 5 and i != 3:  # qq doesnt gen skill point at start
                skill_points += 1
            if check_four_of_a_kind(count_tiles(tiles)):
                break
        print(f"Time: {time:.2f}, Skill Points: {skill_points}, Energy: {qing_que.energy}, Damage: {total_dmg:.2f}")

        if trace2:
            skill_points += 1  # trace 2 gives 1 free skill at start of battle
            trace2 = False

        dmg_percent_buff = 0
        autarky = False
        skills = 0

        while skill_points > 0 and not check_four_of_a_kind(count_tiles(tiles)):
            # Use skill
            new_tiles = draw_tiles(2)
            tiles = update_hand(tiles, new_tiles)
            skill_points -= 1
            skills += 1
            qing_que.energy += 1
            if skills < 4:  # can only get up to 4 buffs from skill
                dmg_percent_buff += (31 + 10)
            if not autarky and random.random() < .24:  # 1st condition avoids dupe prints
                print("autarky")
                autarky = True  # e4: 24% fixed chance for autarky, which doubles basic attack damage

        print("skills: ", skills)
        outcomes["skills"][skills] += 1
        if check_four_of_a_kind(count_tiles(tiles)):  # 4 of a kind
            print("4 of a kind")
            outcomes["hits"] += 1
            tiles = []  # discard hand
            atk_percent_buff = 79  # enter hidden hand state
            if skill_points < 5:
                skill_points += 1
            speed_buff = 10  # A6 trace
            base_dmg = 0
            if qing_que.energy > qing_que.energy_max:  # ult
                print("ult")
                outcomes["ults"] += 1
                base_dmg += qing_que.calculate_base_dmg(qq_ult_mv,
                                                        dmg_percent_buff=dmg_percent_buff + 10,
                                                        atk_percent_buff=atk_percent_buff)
                qing_que.energy = 5
            # auto
            base_dmg += (2 if autarky else 1) * qing_que.calculate_base_dmg(qq_basic2_mv,
                                                                            dmg_percent_buff=dmg_percent_buff,
                                                                            atk_percent_buff=atk_percent_buff)
            outgoing_dmg = base_dmg * toughness_multiplier * def_multiplier
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        else:  # whiff
            base_dmg = 0
            if qing_que.energy > qing_que.energy_max:  # ult, gets you to 4 of a kind
                print("ult")
                outcomes["whiff_ults"] += 1
                base_dmg += qing_que.calculate_base_dmg(qq_ult_mv, dmg_percent_buff=dmg_percent_buff+10)
                tiles = []  # discard hand
                atk_percent_buff = 79  # enter hidden hand state
                skill_points += 1
                qing_que.energy = 5
                base_dmg += (2 if autarky else 1) * qing_que.calculate_base_dmg(qq_basic2_mv,
                                                                                dmg_percent_buff=dmg_percent_buff,
                                                                                atk_percent_buff=atk_percent_buff)
            else:
                print("whiff")
                outcomes["whiffs"] += 1
                base_dmg += (2 if autarky else 1) * qing_que.calculate_base_dmg(qq_basic1_mv,
                                                                                dmg_percent_buff=dmg_percent_buff)
                # discard least common tile
                counts = count_tiles(tiles)
                least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
                tiles.remove(least_common_suit)

            outgoing_dmg = base_dmg * toughness_multiplier * def_multiplier
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        qing_que.energy += 20
        av = 10000 / qing_que.get_speed(percent_buff=speed_buff)
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
        "whiff_ults": 0,
        "whiffs": 0,
    }
    #with disable_print():
    for i in range(num_simulations):
        print(f"Simulation {i + 1}")
        dmg, outcomes = qing_que_simulation()
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
                print(f"{i}: {avg:.2f}")
                average_skills_used += avg * i

            print(f"Average skills used per turn: {average_skills_used / average_turns:.2f}")

        else:
            avg = outcomes_dict[key] / num_simulations
            print(f"{key}: {avg:.2f}")
    print(f"Average turns: {average_turns:.2f}")

    # Display damage distribution using a histogram
    plt.hist(results, bins='auto', edgecolor='black')
    plt.xlabel('Damage')
    plt.ylabel('Frequency')
    plt.title('Damage Distribution')
    plt.show()


if __name__ == "__main__":
    run_simulation()
