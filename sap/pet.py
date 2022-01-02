from dataclasses import dataclass, replace, field

from enum import Enum, auto
from typing import List, Tuple, Optional
from random import Random
import uuid
from abc import ABC, abstractmethod

TeamPair = Tuple[List["Pet"], List["Pet"]]


class TriggerType(Enum):
    # PET TRIGGERS
    PET_FAINTED = auto()
    PET_SUMMONED = auto()
    PET_SOLD = auto()
    PET_BOUGHT = auto()
    PET_LEVELED_UP = auto()
    PET_DAMAGED = auto()
    PET_KNOCKED_OUT_BY = auto()
    PET_EATEN = auto()

    # LIFECYCLE TRIGGERS
    TURN_ENDED = auto()
    BATTLE_STARTED = auto()
    BEFORE_ATTACK = auto()
    AFTER_ATTACK = auto()

    # ACTIONS
    REMOVE_PET = auto()
    SUMMON_PET = auto()
    DEAL_DAMAGE = auto()
    DEAL_DAMAGE_TO_ALL = auto()  # hedgehog
    DEAL_DAMAGE_TO_FRONT = auto()  # rhino
    SUMMON_PET_OTHER_TEAM = auto()
    FAINT_PET = auto()
    REDUCE_HEALTH = auto()
    FORWARD_TRIGGER = auto()  # tiger


@dataclass
class Trigger:
    type: TriggerType
    pet: Optional["Pet"] = None
    summoned_pets: Optional[List["Pet"]] = None
    player: Optional["Player"] = None
    shop: Optional["Shop"] = None
    damage: int = 0
    health_ratio: float = 0
    index: int = 0
    forwarded_trigger: Optional["Trigger"] = None
    trigger_experience: Optional[int] = None
    food: Optional["Food"] = None


@dataclass
class Food(ABC):
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cost: int = 3
    random_gen: Random = Random()

    def feed(self, pet: "Pet", player: "Player"):
        self.apply(pet, player)
        player.apply_trigger(Trigger(TriggerType.PET_EATEN, pet, food=self))

    def summoned_pets(self) -> List["Pet"]:
        return []

    @abstractmethod
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        raise NotImplementedError()


class EquipableFood(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        if pet is None:
            assert ValueError("Can't apply food to None pet")
        pet.equipped_food = self

    def after_attack(self, pet: "Pet"):
        pass

    def attack_bonus(self) -> int:
        return 0

    def reduce_damage(self, damage: int) -> int:
        return damage

    def after_damage(self):
        pass


def pick_unique_pets(
        pets: List["Pet"],
        number: int,
        exclusion: List["Pet"] = None,
        require_living: bool = True,
        random_gen: Random = Random()) -> List["Pet"]:
    if exclusion is None:
        exclusion = []

    picks = []
    if require_living:
        exclusion += [pet for pet in pets if pet.toughness <= 0]
    while len(picks) < number and (len(picks) + len(exclusion)) < len(pets):
        picks.append(random_gen.choice([pet for pet in pets if pet not in exclusion + picks]))

    return picks


@dataclass
class Pet:
    symbol: str
    power: int
    toughness: int
    experience: int = 0
    random_gen: Random = Random()
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    temp_buff_power: int = 0
    temp_buff_toughness: int = 0
    equipped_food: Optional[EquipableFood] = None

    def __repr__(self):
        return f"<{self.symbol}: {self.power} / {self.toughness} ({self.id[:3]})>"

    def combine(self, other: "Pet"):
        if other.symbol != self.symbol:
            raise ValueError("Tried to merge different pet", self, other)
        self.power = max(self.power, other.power) + 1
        self.toughness = max(self.toughness, other.toughness) + 1
        self.experience += other.experience

    def take_damage(self, damage: int) -> int:
        """Have the pet take damage, considering e.g. food, and return the damage actually taken"""
        damage = self.equipped_food.reduce_damage(damage) if self.equipped_food else damage
        self.toughness -= damage
        return damage

    def buff(self, power: int = 0, toughness: int = 0):
        self.power += power
        self.toughness += toughness

    def temp_buff(self, power: int = 0, toughness: int = 0):
        # the temp buff is to keep track of what's temporary or not. We'll get rid of this after the round
        self.temp_buff_power += power
        self.temp_buff_toughness += toughness
        self.power += power
        self.toughness += toughness

    def start_turn(self, player: "Player"):
        """Reset pet after battle, removing e.g. temp bonuses"""
        # Since this modifies the power directly, we can just reuse it to reset the bonuses
        self.temp_buff(power=-self.temp_buff_power, toughness=-self.temp_buff_toughness)

    @property
    def level(self):
        if self.experience < 2:
            return 1
        if 2 <= self.experience < 5:
            return 2
        return 3

    @classmethod
    def spawn(cls):
        return cls(symbol="P", power=1, toughness=1)

    def apply_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:

        # Handle tiger
        triggers = []
        if trigger.type == TriggerType.FORWARD_TRIGGER:
            actual_experience = self.experience
            self.experience = trigger.trigger_experience
            forwarded_trigger = trigger.forwarded_trigger
            triggers = self.apply_trigger(forwarded_trigger, my_team, other_team)
            self.experience = actual_experience
            return triggers  # don't run anything else, we want to run this as if the pet is a different level

        # Handle spawning flies
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            summoned_pets = []
            # Zombie flies
            flies: List[Fly] = []
            if not isinstance(self, ZombieFly):  # can't spawn zombies from zombies, what brains would they eat?
                for pet in my_team:
                    if isinstance(pet, Fly) and pet.num_triggers and pet != self:
                        flies.append(pet)
                        break
            for fly in flies:
                summoned_pets.append(ZombieFly.create(power=5 * fly.level, toughness=5 * fly.level))
                fly.num_triggers -= 1

            # Food triggers
            if self.equipped_food:
                summoned_pets.extend(self.equipped_food.summoned_pets())

            if summoned_pets:
                triggers.append(Trigger(TriggerType.SUMMON_PET, self, summoned_pets=summoned_pets))
        return triggers + self._resolve_trigger(trigger, my_team, other_team)

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        """Default trigger, handle faints"""
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.REMOVE_PET, self))
        return triggers

    def attack(self, other_team: List["Pet"]) -> List[Trigger]:
        """
        Take the pet, and attack the other team. This generates events that can then be resolved.
        """
        food_bonus = self.equipped_food.attack_bonus() if self.equipped_food else 0
        return [Trigger(TriggerType.DEAL_DAMAGE, other_team[0], damage=self.power + food_bonus)]


# Lives in pet to avoid circular imports. TODO: add a way to register triggers rather than inheritance?
class Fly(Pet):
    num_triggers: int = 3

    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=5, symbol="🪰")

    def start_turn(self, player: "Player"):
        super().start_turn(player)
        self.num_triggers = 3

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            self.num_triggers = 3

        # All my spawning happens in the pet itself
        return super()._resolve_trigger(trigger, my_team, other_team)


class ZombieFly(Pet):
    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="🧟🪰")
