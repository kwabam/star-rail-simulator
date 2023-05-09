import random
import matplotlib.pyplot as plt
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


def simulate_skills_to_four_of_a_kind():
    num_tiles_per_skill = 2
    skills = 0
    tiles = draw_tiles(4)

    while not check_four_of_a_kind(count_tiles(tiles)):
        skills += 1

        new_tiles = draw_tiles(num_tiles_per_skill)
        tiles = update_hand(tiles, new_tiles)

    return skills


def simulate_draw_four_discard_one(turns=10000):
    tiles = []
    hits = 0

    for i in range(turns):
        new_tiles = draw_tiles(4)
        tiles = update_hand(tiles, new_tiles)

        if not check_four_of_a_kind(count_tiles(tiles)):
            counts = count_tiles(tiles)
            least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
            tiles.remove(least_common_suit)
        else:  # 4 of a kind, discard hand
            tiles = []
            hits += 1

    return hits


def simulate():
    num_simulations = 10000
    results = [simulate_skills_to_four_of_a_kind() for _ in range(num_simulations)]

    plt.hist(results, bins='auto', edgecolor='black')
    plt.xlabel('Skills required to get 4 of a kind')
    plt.ylabel('Frequency')
    plt.title('Distribution of skills required to get 4 of a kind')
    plt.show()

    print("Average skills required:", sum(results) / num_simulations)

    # Calculate the count and percentage of each result
    counts = {}
    for result in results:
        if result not in counts:
            counts[result] = 0
        counts[result] += 1

    print("Raw count and percentage of each result:")
    for count in sorted(counts):
        percentage = (counts[count] / num_simulations) * 100
        print(f"{count}: {counts[count]} ({percentage:.2f}%)")

    # Calculate the percentage of times it took more than 5 skills
    more_than_five_skills = sum(1 for result in results if result > 5)
    percentage_more_than_five = (more_than_five_skills / num_simulations) * 100
    print(f"Percentage of times it took more than 5 skills: {percentage_more_than_five:.2f}%")


def sub_dps():
    turns = 10000
    hits = simulate_draw_four_discard_one(turns)
    print(f"Percentage of 4-of-a-kinds: {(hits / turns) * 100:.2f}%")


def qing_que_simulation(max_time=850):
    outcomes = {
        "skills": [0, 0, 0, 0, 0, 0, 0],
        "hits": 0,
        "whiff_ults": 0,
        "whiffs": 0,
    }

    the_seriousness_of_breakfast = Lightcone(
        80,
        846,
        476,
        396
    )
    character = Character(
        level=80,
        base_hp=1023,
        base_atk=652,
        base_def=441,
        base_speed=98,
        flat_hp=705,
        flat_atk=352,
        flat_speed=25,
        percent_atk=43.2 + 28 + 3.85 * 4,
        percent_def=12.5,
        crit_rate=5 + 32.4 + 2.85 * 10,
        crit_dmg=50 + 5.75 * 10,
        dmg_percent=10 + 14.4 + 38.88 + 24,  # breakfast
        lightcone=the_seriousness_of_breakfast,
        energy_max=140
    )

    enemy_level = 80
    enemy_def = 200 + 10 * enemy_level
    enemy_def = .8 * enemy_def  # quantum set
    def_multiplier = 1 - (enemy_def / (enemy_def + 200 + 10 * character.level))

    total_dmg = 0

    qq_basic1_mv = 1
    qq_basic2_mv = 2.64

    qq_ult_mv = 2.16 * 1.1
    speed_buff = 0

    trace2 = True

    skill_points = 3

    tiles = []

    time = 10000 / character.get_speed()
    while time < max_time:
        for i in range(4):  # draw 1 tile for each teammate and 1 for self
            tiles = update_hand(tiles, draw_tiles(1))
            character.energy += 1
            if skill_points < 5 and i != 3:  # qq doesnt gen skill point at start
                skill_points += 1
            if check_four_of_a_kind(count_tiles(tiles)):
                break
        print(f"Time: {time:.2f}, Skill Points: {skill_points}, Energy: {character.energy}, Damage: {total_dmg:.2f}")

        if trace2:
            skill_points += 1  # trace 2 gives 1 free skill at start of battle
            trace2 = False

        av = 10000 / character.get_speed(percent_buff=speed_buff)
        speed_buff = 0
        dmg_percent_buff = 0
        e4 = 1
        skills = 0

        while skill_points > 0 and not check_four_of_a_kind(count_tiles(tiles)):
            # Use skill
            new_tiles = draw_tiles(2)
            tiles = update_hand(tiles, new_tiles)
            skill_points -= 1
            skills += 1
            if skills < 4:
                dmg_percent_buff += (31 + 10)
            if random.random() < .24 and e4 == 1:
                print("autarky")
                e4 = 2  # 24% fixed chance for autarky, which doubles damage

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
            if character.energy > character.energy_max and e4 == 2:  # ult
                print("ult")
                base_dmg += qq_ult_mv * character.get_atk(percent_buff=atk_percent_buff)
                character.energy = 5
            # auto
            base_dmg += qq_basic2_mv * character.get_atk(percent_buff=atk_percent_buff)
            outgoing_dmg = e4 * base_dmg * character.get_dmg_multiplier(
                dmg_percent_buff=dmg_percent_buff) * def_multiplier * character.get_crit_multiplier()
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        else:  # whiff
            base_dmg = 0
            if character.energy > character.energy_max:  # ult, gets you to 4 of a kind
                print("ult")
                outcomes["whiff_ults"] += 1
                base_dmg += qq_ult_mv * character.get_atk()
                tiles = []  # discard hand
                atk_percent_buff = 79  # enter hidden hand state
                skill_points += 1
                character.energy = 5
                base_dmg += qq_basic2_mv * character.get_atk(percent_buff=atk_percent_buff)
            else:
                print("whiff")
                outcomes["whiffs"] += 1
                base_dmg += qq_basic1_mv * character.get_atk()
                # discard least common tile
                counts = count_tiles(tiles)
                least_common_suit = min((suit for suit in counts if counts[suit] > 0), key=counts.get)
                tiles.remove(least_common_suit)


            outgoing_dmg = e4 * base_dmg * character.get_dmg_multiplier(
                dmg_percent_buff=dmg_percent_buff) * def_multiplier * character.get_crit_multiplier()
            print("outgoing dmg: ", outgoing_dmg)
            total_dmg += outgoing_dmg
        character.energy += 20
        time += av
    return total_dmg, outcomes


def run_simulation(num_simulations=10000):
    results = []
    outcomes_dict = {
        "skills": [0, 0, 0, 0, 0, 0, 0],
        "whiff_ults": 0,
        "whiffs": 0,
    }
    with disable_print():
        for _ in range(num_simulations):
            dmg, outcomes = qing_que_simulation()
            results.append(dmg)

            for key in outcomes_dict:
                if key == "skills":
                    for i in range(len(outcomes[key])):
                        outcomes_dict[key][i] += outcomes[key][i]
                else:
                    outcomes_dict[key] += outcomes[key]

    # Calculate average damage and display it
    average_dmg = sum(results) / num_simulations
    print(f"Average damage: {average_dmg:.2f}")

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

            print(f"Average skills used per turn: {average_skills_used/average_turns:.2f}")

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
