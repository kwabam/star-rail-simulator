from dataclasses import dataclass, fields
import json
from typing import Optional
import requests



base_url = "https://raw.githubusercontent.com/Dimbreath/StarRailData/master/ExcelOutput"

key_map = {
    'HPDelta': 'flat_hp',
    'AttackDelta': 'flat_atk',
    'DefenceDelta': 'flat_def',
    'SpeedDelta': 'flat_speed',
    'HPAddedRatio': 'percent_hp',
    'AttackAddedRatio': 'percent_atk',
    'DefenceAddedRatio': 'percent_def',
    'CriticalChanceBase': 'crit_rate',
    'CriticalDamageBase': 'crit_dmg',
    'StatusProbabilityBase': 'effect_hit_rate',
    'StatusResistanceBase': 'effect_res',
    'BreakDamageAddedRatioBase': 'break_effect',
    'PhysicalAddedRatio': 'percent_dmg',
    'FireAddedRatio': 'percent_dmg',
    'IceAddedRatio': 'percent_dmg',
    'ThunderAddedRatio': 'percent_dmg',
    'WindAddedRatio': 'percent_dmg',
    'QuantumAddedRatio': 'percent_dmg',
    'ImaginaryAddedRatio': 'percent_dmg',
    'SPRatioBase': 'energy_regeneration_rate',
    'HealRatioBase': 'percent_heal'
}

terms = ["Critical", "Ratio", "Resistance"]  # stats that are percentages
percent_stats = {key for key in key_map if any(term in key for term in terms)}


@dataclass
class SubStats:
    flat_hp: Optional[int] = 0
    flat_atk: Optional[int] = 0
    flat_def: Optional[int] = 0
    flat_speed: Optional[int] = 0
    percent_hp: Optional[float] = 0
    percent_atk: Optional[float] = 0
    percent_def: Optional[float] = 0
    crit_rate: Optional[float] = 0
    crit_dmg: Optional[float] = 0

    def __post_init__(self):
        relic_sub_affix_dict = load_relic_sub_affix_config()
        for field in fields(self):
            field_value = relic_sub_affix_dict.get(field.name, 0)
            setattr(self, field.name, getattr(self, field.name) * field_value)


@dataclass
class MainStats:
    flat_hp: Optional[int] = 0
    flat_atk: Optional[int] = 0
    flat_def: Optional[int] = 0
    flat_speed: Optional[int] = 0
    percent_hp: Optional[float] = 0
    percent_atk: Optional[float] = 0
    percent_def: Optional[float] = 0
    percent_dmg: Optional[float] = 0
    percent_heal: Optional[float] = 0
    crit_rate: Optional[float] = 0
    crit_dmg: Optional[float] = 0
    energy_regeneration_rate: Optional[float] = 0

    def __post_init__(self):
        relic_main_affix_dict = load_relic_main_affix_config()
        for field in fields(self):
            field_value = relic_main_affix_dict.get(field.name, 0)
            setattr(self, field.name, getattr(self, field.name) * field_value)


def load_relic_sub_affix_config():
    relic_url = base_url + '/RelicSubAffixConfig.json'
    response = requests.get(relic_url)
    data = json.loads(response.text)


    result = {}
    for key, entry in data["5"].items():
        property_name = entry['Property']
        base_value = entry['BaseValue']['Value']
        step_value = entry['StepValue']['Value']
        num_steps = entry['StepNum']
        calculated_value = base_value + step_value * (num_steps / 2)
        if property_name in percent_stats:
            calculated_value *= 100

        remapped_key = key_map.get(property_name, property_name)
        result[remapped_key] = calculated_value
    return result


def load_relic_main_affix_config():
    relic_url = base_url + '/RelicMainAffixConfig.json'
    response = requests.get(relic_url)
    data = json.loads(response.text)

    result = {}
    for _, entry in data.items():
        for item_properties in entry.values():
            property_name = item_properties['Property']
            base_value = item_properties['BaseValue']['Value']
            level_add = item_properties['LevelAdd']['Value']
            calculated_value = base_value + level_add * 15
            if property_name in percent_stats:
                calculated_value *= 100
            remapped_key = key_map.get(property_name, property_name)
            result[remapped_key] = max(result.get(remapped_key, 0), calculated_value)

    return result


if __name__ == "__main__":
    relic_sub_affix_dict = load_relic_sub_affix_config()
    print(relic_sub_affix_dict)
    relic_main_affix_dict = load_relic_main_affix_config()
    print(relic_main_affix_dict)
    print()
    print(SubStats(flat_hp=4, crit_rate=10, crit_dmg=10))
    print(MainStats(flat_hp=1, crit_rate=1, crit_dmg=1))
