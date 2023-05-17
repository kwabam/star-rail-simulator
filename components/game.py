from dataclasses import dataclass
from abc import ABC
from typing import List
from components.character import Character, modify_field


@dataclass
class Action:
    character: Character
    av: int

class Game(ABC):
    def __init__(self, team: List[Character], enemy_level: int = 80, time_limit: int = 850, skill_points: int = 3):
        self.team = team
        self.enemy_level = enemy_level
        self.time_limit = time_limit
        self.time = 0
        self.total_damage = 0
        self.skill_points = skill_points
        self.buffs = {}
        self.action_queue = []
        self.current_character = None
        for character in sorted(self.team, key=lambda c: c.get_speed(), reverse=True):
            av = 10000 / character.get_speed()
            character.game = self
            self.action_queue.append(Action(character, av))


    def add_aoe_buff(self, buff_name: str, buff_type: str, buff_value: float,
                 duration: int, max_instances: int = 1):
        for character in self.team:
            self.add_buff(character, buff_name, buff_type, buff_value, duration, max_instances)


    def add_buff(self, character: Character, buff_name: str, buff_type: str, buff_value: float,
                 duration: int, max_instances: int = 1):
        if character not in self.buffs:
            self.buffs[character] = []

        existing_buffs_count = 0
        oldest_buff_index = None
        oldest_duration = None

        # Most buffs have a limit of how many times they can be applied
        # Check through list of existing buffs to see if the buff is already applied
        for i, (existing_buff_name, existing_buff_type, existing_buff_value, existing_duration) in enumerate(
                self.buffs[character]):
            if buff_name == existing_buff_name:
                existing_buffs_count += 1
                if oldest_duration is None or existing_duration < oldest_duration:
                    oldest_duration = existing_duration
                    oldest_buff_index = i

        if existing_buffs_count >= max_instances:
            # If the maximum number of instances is reached, refresh the oldest buff
            self.buffs[character][oldest_buff_index] = (buff_name, buff_type, buff_value, duration)
        else: # apply the buff to character
            modify_field(character, buff_type, buff_value)
            self.buffs[character].append((buff_name, buff_type, buff_value, duration))

    def process_buffs(self, character: Character):
        if character in self.buffs:
            new_buffs = []
            for buff_name, buff_type, buff_value, turns_remaining in self.buffs[character]:
                turns_remaining -= 1
                if turns_remaining > 0:
                    # update the buff with new turns_remaining value
                    new_buffs.append((buff_name, buff_type, buff_value, turns_remaining))
                else:
                    # remove buff from character's stats
                    modify_field(character, buff_type, -buff_value)
            # update the character's buffs with the new_buffs list
            self.buffs[character] = new_buffs


    def advance(self, character, percentage):
        for action in self.action_queue:
            if action.character == character:
                time_to_action = action.av - self.time
                action.av = self.time + time_to_action * (1 - percentage/100)


    def add_character_to_action_queue(self, character):
        av = 10000 / character.get_speed()
        self.action_queue.append(Action(character, self.time + av))

    def add_skill_point(self):
        if self.skill_points < 5:
            self.skill_points += 1

    def play(self):
        while True:
            # Sort the action queue by action value (av)
            # Not efficient, but simple way to track action queue
            self.action_queue.sort(key=lambda x: x.av)

            action = self.action_queue.pop(0)
            self.current_character = action.character
            self.time = action.av

            if self.time >= self.time_limit:
                break

            print(f"Time: {self.time} | Character: {self.current_character.character_name}")
            if self.current_character in self.buffs:
                print(f"Buffs: {self.buffs[self.current_character]}")

            self.current_character.act()
            if len(self.action_queue) == 0 or \
                    self.action_queue[-1].character != self.current_character: # some people advance forward their action
                self.action_queue.append(Action(self.current_character, action.av + 10000 / self.current_character.get_speed()))
            self.process_buffs(self.current_character)

            # Update the character's action value and re-insert them into the action queue
            print("========================================================")
        print(f"Total Damage: {self.total_damage}")

    def add_damage(self, damage: int):
        enemy_def = (200 + 10 * self.enemy_level) * (1 - self.current_character.percent_def_ignore/100)
        def_multiplier = 1 - (enemy_def/(enemy_def + 200 + 10 * self.current_character.level))
        resistance_multiplier = 1 + self.current_character.percent_penetration / 100
        toughness_multiplier = .9
        damage = damage * def_multiplier * resistance_multiplier * toughness_multiplier
        print(f"Added damage: {damage}")
        self.total_damage += damage
