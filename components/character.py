import random

import requests
import json
import logging
from components.lightcones import Lightcone
from abc import ABC, abstractmethod
from dataclasses import fields
from components.stats import MainStats, SubStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_url = "https://raw.githubusercontent.com/KQM-git/SRL/master/src/data"


class Character(ABC):
    def __init__(self, character_name, lightcone, main_stats, sub_stats, energy_max=100, ascension=6, level=80, random_crits=False):
        character_data_url = f"{base_url}/characters/{parse_name(character_name)}.json"
        response = requests.get(character_data_url)
        if response.status_code == 200:
            data = json.loads(response.text)
        else:
            logger.error(f"Error: Unable to download JSON file. Status code: {response.status_code}")
        character_data = data['stats'][ascension]
        if 'energyMax' not in character_data.keys():
            character_data['energyMax'] = energy_max

        # decides whether to roll for crits or whether to use average hit damage
        self.random_crits = random_crits

        self.game = None

        self.character_name = character_name

        self.level = level
        self.lightcone = lightcone
        self.damage_type = data['damageType']
        self.base_type = data['baseType']
        self.base_hp = character_data['hpBase'] + (character_data['hpAdd'] * level)
        self.base_atk = character_data['attackBase'] + (character_data['attackAdd'] * level)
        self.base_def = character_data['defenseBase'] + (character_data['defenseAdd'] * level)
        self.base_speed = character_data['speedBase'] + (character_data['speedAdd'] * level)
        self.flat_hp = 0
        self.flat_atk = 0
        self.flat_def = 0
        self.flat_speed = 0
        self.percent_hp = 0
        self.percent_atk = 0
        self.percent_def = 0
        self.percent_speed = 0
        self.percent_dmg = 0
        self.percent_heal = 0
        self.crit_rate = 100 * character_data['crate']
        self.crit_dmg = 100 * character_data['cdmg']
        self.percent_penetration = 0
        self.percent_def_ignore = 0
        self.energy_regeneration_rate = 0
        self.energy_max = character_data['energyMax']
        self.aggro = character_data['aggro']

        add_fields(self, lightcone, exclude=['level'])
        add_fields(self, main_stats)
        add_fields(self, sub_stats)
        for boost, value in find_trace_boosts(data['skillTree']):
            if 'DEF' in boost:
                self.percent_def += value * 100
            elif 'ATK' in boost:
                self.percent_atk += value * 100
            elif 'CRIT DMG' in boost:
                self.crit_dmg += value * 100
            elif 'CRIT' in boost:
                self.crit_rate += value * 100
            elif 'DMG' in boost:
                self.percent_dmg += value * 100

        self.energy = self.energy_max / 2

    def get_hp(self):
        return self.base_hp * (1 + self.percent_hp) + self.flat_hp

    def get_atk(self, flat_buff=0, percent_buff=0):
        return self.base_atk * (100 + self.percent_atk + percent_buff) / 100 + self.flat_atk + flat_buff

    def get_def(self, flat_buff=0, percent_buff=0):
        return self.base_def * (100 + self.percent_def + percent_buff) / 100 + self.flat_def + flat_buff

    def get_speed(self, flat_buff=0, percent_buff=0):
        return self.base_speed * (100 + self.percent_speed + percent_buff) / 100 + self.flat_speed + flat_buff

    def get_average_crit_multiplier(self, crit_rate_buff=0, crit_dmg_buff=0):
        return 1 + (self.crit_rate / 100 * self.crit_dmg / 100)

    def get_crit_rate(self, crit_rate_buff=0):
        return (self.crit_rate + crit_rate_buff) / 100

    def get_crit_damage_multiplier(self, crit_dmg_buff=0):
        return 1 + ((self.crit_dmg + crit_dmg_buff) / 100)

    def get_dmg_multiplier(self, dmg_percent_buff=0):
        return (100 + self.percent_dmg + dmg_percent_buff) / 100

    def add_energy(self, energy):
        self.energy += energy * (1 + self.energy_regeneration_rate / 100)

    def calculate_base_dmg(self, mv, atk_percent_buff=0, dmg_percent_buff=0, crit_rate_buff=0, crit_dmg_buff=0):
        if self.random_crits: # simulate crits and non crits
            if random.random() < self.get_crit_rate(crit_rate_buff=crit_rate_buff):  # if you crit
                mv *= self.get_crit_damage_multiplier(crit_dmg_buff=crit_dmg_buff)  # multiply by crit damage multiplier
        else:
            mv *= self.get_average_crit_multiplier() # just multiply by average crit multiplier
        return mv \
            * self.get_atk(percent_buff=atk_percent_buff) \
            * self.get_dmg_multiplier(dmg_percent_buff=dmg_percent_buff)

    @abstractmethod
    def act(self):
        pass

    @abstractmethod
    def basic(self):
        pass

    @abstractmethod
    def skill(self):
        pass

    @abstractmethod
    def ult(self):
        pass


def modify_field(character, field_name, value):
    base_field_value = getattr(character, field_name)
    setattr(character, field_name, base_field_value + value)


def add_fields(character, source, exclude=None):
    if exclude is None:
        exclude = []

    fields_to_add = [field.name for field in fields(source) if field.name not in exclude]
    for field_name in fields_to_add:
        modify_field(character, field_name, getattr(source, field_name, 0))


def find_trace_boosts(skill_tree):
    trace_boosts = []
    for entry in skill_tree:
        if 'Boost' in entry['name']:
            trace_boosts.append((entry['name'], entry['params'][0]))
        if 'children' in entry:
            trace_boosts.extend(find_trace_boosts(entry['children']))
    return trace_boosts


def parse_name(name):
    # trailblazer has some wack names
    if name == "fmc":
        return "Trailblazer_(Fire)"
    elif name == "pmc":
        return "Trailblazer_(Physical)"
    return name.title().replace(" ", "_")
