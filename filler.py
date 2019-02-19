#!/usr/bin/env python3


from helper import Source, Dice, Speed, Armor, Ability, Abilities, Attack, \
    Trait, Action, Monster, Range
import importer
from typing import List, Tuple


desired_monsters: List[Tuple[str, int]] = [
    ('Aarakocra', 3),
    ('Bone Naga (Guardian)', 2),
    ('Gnoll', 4),
]
# for name, count in desired_monsters:
#     print(importer.get_monster(name))

print('''
%FDF-1.2
1 0 obj<</FDF<< /Fields[
'''.strip('\n'))


def output_field(field_name, field_value):
    print('<< /T({})/V({}) >>'.format(field_name, field_value))


def format_modifier(modifier: int) -> str:
    if modifier < 0:
        return str(modifier)
    else:
        return '+' + str(modifier)


def format_range(range: Range) -> str:
    result = []
    if range.melee is not None:
        result.append("{}'".format(range.melee.range))
    if range.ranged is not None:
        part = "{}'".format(range.ranged.short)
        if range.ranged.long is not None:
            part += "/{}'".format(range.ranged.long)
        result.append(part)
    return ' or '.join(result)


def format_dice(dice: Dice) -> str:
    return '{}d{}'.format(dice.count, dice.faces)


def format_hit_dice(monster: Monster) -> str:
    result = format_dice(monster.hit_dice)
    modifier = monster.hit_dice.count * monster.abilities.constitution.raw_modifier
    if modifier < 0:
        result += str(modifier)
    elif modifier > 0:
        result += '+' + str(modifier)
    return result


def format_speeds(monster: Monster) -> str:
    speed_strings = []
    for kind, speed in monster.speeds.items():
        result = ''
        if kind is not None:
            result += kind + ' '
        result += str(speed.value) + "'"
        if speed.info:
            result += speed.info
        speed_strings.append(result)

    speed_strings.sort()
    return '\r'.join(speed_strings)

def format_multiline(min_lines: int, value: str) -> str:
    lines = value.splitlines()
    while len(lines) < min_lines:
        lines.append('')
    return '\r'.join(lines)

total_xp = 0
total_monster_count = 0

monster_index = 0
for monster_name, count in desired_monsters:
    monster_index += 1
    monster = importer.get_monster(monster_name)

    total_xp += monster.xp * count
    total_monster_count += count

    fields: List[Tuple[str, str]] = [
        ('monster_{}_name'.format(monster_index), monster.name + (' x {}'.format(count) if count != 1 else '')),
        ('monster_{}_size'.format(monster_index), monster.size),
        ('monster_{}_ac'.format(monster_index), str(monster.armor.armor_class)),
        ('monster_{}_armortype'.format(monster_index), monster.armor.type),
        ('monster_{}_race'.format(monster_index), monster.race),
        ('monster_{}_alignment'.format(monster_index), monster.alignment),
        ('monster_{}_basehp'.format(monster_index), str(monster.base_hp)),
        ('monster_{}_hitdice'.format(monster_index), format_hit_dice(monster)),
        ('monster_{}_speed'.format(monster_index), format_speeds(monster)),
        ('monster_{}_passiveperception'.format(monster_index), str(monster.passive_perception)),
        ('monster_{}_proficiencybonus'.format(monster_index), monster.proficiency_bonus),

        ('monster_{}_str_score'.format(monster_index), str(monster.abilities.strength.score)),
        ('monster_{}_str_mod'.format(monster_index), monster.abilities.strength.modifier),
        ('monster_{}_str_save'.format(monster_index), monster.abilities.strength.save),

        ('monster_{}_dex_score'.format(monster_index), str(monster.abilities.dexterity.score)),
        ('monster_{}_dex_mod'.format(monster_index), monster.abilities.dexterity.modifier),
        ('monster_{}_dex_save'.format(monster_index), monster.abilities.dexterity.save),

        ('monster_{}_con_score'.format(monster_index), str(monster.abilities.constitution.score)),
        ('monster_{}_con_mod'.format(monster_index), monster.abilities.constitution.modifier),
        ('monster_{}_con_save'.format(monster_index), monster.abilities.constitution.save),

        ('monster_{}_int_score'.format(monster_index), str(monster.abilities.intelligence.score)),
        ('monster_{}_int_mod'.format(monster_index), monster.abilities.intelligence.modifier),
        ('monster_{}_int_save'.format(monster_index), monster.abilities.intelligence.save),

        ('monster_{}_wis_score'.format(monster_index), str(monster.abilities.wisdom.score)),
        ('monster_{}_wis_mod'.format(monster_index), monster.abilities.wisdom.modifier),
        ('monster_{}_wis_save'.format(monster_index), monster.abilities.wisdom.save),

        ('monster_{}_cha_score'.format(monster_index), str(monster.abilities.charisma.score)),
        ('monster_{}_cha_mod'.format(monster_index), monster.abilities.charisma.modifier),
        ('monster_{}_cha_save'.format(monster_index), monster.abilities.charisma.save),
    ]

    traits_parts: List[str] = [
        'CR: {}'.format(monster.challenge_rating),
        'XP: {}'.format(monster.xp),
    ]

    if monster.skills is not None:
        traits_parts.append(monster.skills)
    if monster.senses is not None:
        traits_parts.append(monster.senses)
    traits_parts.extend([
        '{}: {}'.format(trait.name, trait.description)
        for trait in monster.traits
    ])
    if monster.spells:
        traits_parts.append('Spellcasting')
    traits_parts.extend([
        spell
        for spell in monster.spells
    ])
    traits_parts.extend([
        '{}: {}'.format(action.name, action.description)
        for action in monster.actions
    ])

    fields.append(('monster_{}_traits'.format(monster_index), '\r'.join(traits_parts)))

    for index, attack in enumerate(monster.attacks):
        fields += [
            ('monster_{}_attack_{}_name'.format(monster_index, index+1), attack.name),
            ('monster_{}_attack_{}_tohit'.format(monster_index, index+1), attack.ability.modifier),
            ('monster_{}_attack_{}_damage'.format(monster_index, index+1), '{}{} {}'.format(format_dice(attack.damage), format_modifier(attack.ability.raw_modifier + monster.raw_proficiency_bonus), attack.damage_type)),
            ('monster_{}_attack_{}_tohit'.format(monster_index, index+1), attack.ability.modifier),
            ('monster_{}_attack_{}_range'.format(monster_index, index+1), format_range(attack.range)),
            ('monster_{}_attack_{}_description'.format(monster_index, index+1), format_multiline(3, attack.description)),
        ]

    for field_name, field_value in fields:
        output_field(field_name, field_value)


encounter_multipliers = {
    0: 0.0,
    1: 1.0,
    2: 1.5,
    3: 2.0,
    4: 2.0,
    5: 2.0,
    6: 2.0,
    7: 2.5,
    8: 2.5,
    9: 2.5,
    10: 2.5,
    11: 3.0,
    12: 3.0,
    13: 3.0,
    14: 3.0,
    15: 4.0,
}


multiplier = encounter_multipliers[total_monster_count] if total_monster_count in encounter_multipliers else encounter_multipliers[15]
output_field('encounter_xp', '{} (Adj. {})'.format(total_xp, int(multiplier * total_xp)))


print('''
] >> >>
endobj
trailer
<</Root 1 0 R>>
%%EOF
'''.strip('\n'))
