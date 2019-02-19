from typing import Any, Dict, List, Iterable, Optional
from helper import Source, Dice, Speed, Armor, Ability, Abilities, Attack, \
    Trait, Action, Monster, Range, MeleeRange, RangedRange
import json
import glob
import os
import re


def parse_speed(speed: str, name: str) -> Dict[Optional[str], Speed]:
    regex = re.compile(r'\s*(\D\w*)?\s*(\d+)\s*ft\s*(\([^\)]*\))?(?:,)?\s*')

    remaining = speed
    kinds = {}  # type: Dict[Optional[str], Speed]
    while remaining != '':
        match = regex.search(remaining)
        if match is None:
            raise ValueError(
                'Failed parsing speed string ' + remaining + ' under ' + name)
        else:
            type, value, info = match.groups()
            remaining = remaining[match.end():]
            kinds[type] = Speed(value=int(value), info=info)
    return kinds


def parse_range(range_string: Optional[str]) -> Range:
    if range_string is None or range_string == '':
        return Range(None, None)

    regex = re.compile(r'(Melee) \((\d+) ft\)|(Ranged) \((\d+)(?:/(\d+))? ft\)')
    match = regex.match(range_string)
    if match is None:
        raise ValueError('Failed to match range: ' + range_string)
    is_melee, reach, is_ranged, range_short, range_long = match.groups()

    melee_range = MeleeRange(int(reach)) if is_melee is not None else None
    ranged_range = RangedRange(int(range_short),
                               int(range_long) if range_long is not None
                               else None) if is_ranged is not None else None
    return Range(melee_range, ranged_range)


# TODO May not need this anymore with the four-attack sheet.
def merge_attacks(attacks: List[Attack]) -> List[Attack]:
    attacks_by_base_name = {}  # type: Dict[str, List[Attack]]

    for attack in attacks:
        paren_pos = attack.name.find('(')
        if paren_pos >= 0:
            base_name = attack.name[:paren_pos].strip()
        else:
            base_name = attack.name
        if base_name not in attacks_by_base_name:
            attacks_by_base_name[base_name] = []
        attacks_by_base_name[base_name].append(attack)

    def check_all_equal(iterator: Iterable[Any]) -> bool:
        iterator = iter(iterator)
        try:
            first = next(iterator)
        except StopIteration:
            return True
        return all(first == rest for rest in iterator)

    def merge_ranges(ranges: List[Range]) -> Range:
        result = Range(None, None)
        for range in ranges:
            if range.melee is not None:
                result.melee = range.melee
            if range.ranged is not None:
                result.ranged = range.ranged
        return result

    def merge_attack_list(similar_attacks: List[Attack], base_name) -> List[Attack]:
        abilities = list(map(lambda attack: attack.ability, similar_attacks))
        damages = list(map(lambda attack: attack.damage, similar_attacks))
        damage_types = list(map(lambda attack: attack.damage_type, similar_attacks))
        ranges = list(map(lambda attack: attack.range, similar_attacks))
        descriptions = list(map(lambda attack: attack.description, similar_attacks))

        if not (check_all_equal(abilities) and check_all_equal(damages)
                and check_all_equal(damage_types)):
            return similar_attacks
        if not check_all_equal(descriptions):
            description = '\n'.join(descriptions)
        else:
            description = descriptions[0]

        return [
            Attack(
                name=base_name,
                ability=abilities[0],
                damage=damages[0],
                damage_type=damage_types[0],
                range=merge_ranges(ranges),
                description=description
            )
        ]

    merged_attacks = {
        base_name: merge_attack_list(similar_attacks, base_name)
        for base_name, similar_attacks in attacks_by_base_name.items()
    }

    return [attack for attack_list in merged_attacks.values() for attack in attack_list]


def parse_monster(json_object: dict) -> Monster:
    speeds = parse_speed(json_object['speed'], json_object['name'])

    scores = json_object['scores']
    saves = json_object['saves']
    ability_list: List[Ability] = [Ability(score=score, save=save
                                           if isinstance(save, int) else None)
                                   for score, save in zip(scores, saves)]
    abilities = Abilities(*ability_list)

    attacks = [
        Attack(
            attack['name'],
            ability_list[attack['ability'] - 1],
            Dice(attack['damage'][0], attack['damage'][1]),
            attack['damage'][2],
            parse_range(attack.get('range')),
            attack['description'])
        for attack in json_object['attacks']
    ]
    attacks = merge_attacks(attacks)

    traits = [
        Trait(
            trait['name'],
            trait['description']
        )
        for trait in json_object.get('traits', [])
    ]
    actions = [
        Action(
            action['name'],
            action['description']
        )
        for action in json_object.get('actions', [])
    ]

    cr = json_object['challenge_rating']

    return Monster(
        name=json_object['name'],
        source=Source(*json_object['source']),
        size=json_object['size'],
        race=json_object['type'],
        alignment=json_object['alignment'],  # TODO abbreviated alignment
        armor=Armor(*json_object['ac']),
        base_hp=json_object['hp'],
        hit_dice=Dice(*json_object['hd']),
        speeds=speeds,
        abilities=abilities,
        spells=json_object.get('spells', []),
        skills=json_object.get('skills'),
        senses=json_object.get('senses'),
        passive_perception=json_object['passive_perception'],
        languages=json_object['languages'].split(',') if 'languages' in json_object else [],
        challenge_rating=cr,
        attacks=attacks,
        traits=traits,
        actions=actions,
    )


def import_manual(manual_path: str) -> Dict[str, Monster]:
    with open(manual_path, 'rb') as fd:
        data = json.load(fd)

    monsters = {}
    for monster_data in data.values():
        monster = parse_monster(monster_data)
        monsters[monster.name.lower()] = monster
    return monsters


manual_files = glob.glob('Encounter-Sheet-Imports/_manuals/**/*.json',
                         recursive=True)
monsters = {}
for manual_file in manual_files:
    monsters.update(import_manual(os.path.join(os.path.dirname(__file__),
                                               manual_file)))


# max_attacks = 0
# for name, monster in monsters.items():
#     number_of_attacks = len(monster.attacks)
#     if number_of_attacks > 3:
#         print(name, 'from', monster.source.book, 'has', number_of_attacks, 'attacks')


def get_monster(name: str) -> Monster:
    return monsters[name.lower()]
