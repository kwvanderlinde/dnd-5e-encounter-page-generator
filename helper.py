import attr
from typing import Dict, List, Optional, Tuple, Union


challenge_rating_mapping: Dict[str, Tuple[int, int]] = {
    '0': (2, 10),
    '1/8': (2, 25),
    '1/4': (2, 50),
    '1/2': (2, 100),
    '1': (2, 200),
    '2': (2, 450),
    '3': (2, 700),
    '4': (2, 1100),
    '5': (3, 1800),
    '6': (3, 2300),
    '7': (3, 2900),
    '8': (3, 3900),
    '9': (4, 5000),
    '10': (4, 5900),
    '11': (4, 7200),
    '12': (4, 8400),
    '13': (5, 10000),
    '14': (5, 11500),
    '15': (5, 13000),
    '16': (5, 15000),
    '17': (6, 18000),
    '18': (6, 20000),
    '19': (6, 22000),
    '20': (6, 25000),
    '21': (7, 33000),
    '22': (7, 41000),
    '23': (7, 50000),
    '24': (7, 62000),
    '25': (8, 75000),
    '26': (8, 90000),
    '27': (8, 105000),
    '28': (8, 120000),
    '29': (9, 135000),
    '30': (9, 155000),
}


@attr.s(auto_attribs=True)
class Source:
    book: str
    page: int


@attr.s(auto_attribs=True)
class Dice:
    count: int
    faces: int


@attr.s(auto_attribs=True)
class Speed:
    value: int
    info: str


@attr.s(auto_attribs=True)
class Armor:
    armor_class: int
    type: str
    has_shield: bool


@attr.s(auto_attribs=True)
class Ability:
    score: int
    _save: Optional[int]

    @property
    def save(self) -> str:
        diff = self._save if self._save is not None else self.raw_modifier
        if diff < 0:
            return str(diff)
        return '+{}'.format(diff)

    @property
    def raw_modifier(self) -> int:
        return (self.score - 10) // 2

    @property
    def modifier(self) -> str:
        diff = self.raw_modifier
        if diff < 0:
            return str(diff)
        return '+{}'.format(diff)


@attr.s(auto_attribs=True)
class Abilities:
    strength: Ability
    dexterity: Ability
    constitution: Ability
    intelligence: Ability
    wisdom: Ability
    charisma: Ability


@attr.s(auto_attribs=True)
class MeleeRange:
    range: int


@attr.s(auto_attribs=True)
class RangedRange:
    short: int
    long: Optional[int]


@attr.s(auto_attribs=True)
class Range:
    melee: Optional[MeleeRange]
    ranged: Optional[RangedRange]


@attr.s(auto_attribs=True)
class Attack:
    name: str
    ability: Ability
    damage: Dice
    damage_type: str
    range: Range
    description: str


@attr.s(auto_attribs=True)
class Trait:
    name: str
    description: str


@attr.s(auto_attribs=True)
class Action:
    name: str
    description: str


@attr.s(auto_attribs=True)
class Monster:
    name: str
    source: Source
    size: str
    race: str
    alignment: str
    armor: Armor
    base_hp: int
    hit_dice: Dice
    speeds: Dict[Optional[str], Speed]
    abilities: Abilities
    spells: List[str]
    skills: Optional[str]
    senses: Optional[str]
    passive_perception: int
    languages: List[str]
    challenge_rating: str  # TODO Have a type for CR
    attacks: List[Attack]
    traits: List[Trait]
    actions: List[Action]

    @property
    def raw_proficiency_bonus(self) -> int:
        return challenge_rating_mapping[self.challenge_rating][0]

    @property
    def proficiency_bonus(self) -> str:
        diff = self.raw_proficiency_bonus
        if diff < 0:
            return str(diff)
        else:
            return '+' + str(diff)

    @property
    def xp(self) -> int:
        return challenge_rating_mapping[self.challenge_rating][1]
