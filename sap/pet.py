from dataclasses import dataclass, field

from enum import Enum, auto
from typing import List, Tuple, Optional
from random import Random
import uuid
from abc import ABC, abstractmethod

TeamPair = Tuple[List["Pet"], List["Pet"]]


MAX_POWER = 50
MAX_TOUGHNESS = 50

class TriggerType(Enum):
    # PET TRIGGERS
    PET_FAINTED = auto()
    PET_SUMMONED = auto()
    PET_SOLD = auto()
    PET_BOUGHT = auto()
    PET_LEVELED_UP = auto()
    PET_DAMAGED = auto()
    PET_KNOCKED_OUT_BY = auto()
    PET_EATEN_SHOP_FOOD = auto()

    # LIFECYCLE TRIGGERS
    TURN_STARTED = auto()
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
    DEAL_POISON_DAMAGE = auto()  # scorpion
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
    symbol: str
    cost: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    random_gen: Random = Random()
    power: int = 0
    toughness: int = 0

    def __repr__(self):
        return f"<{self.symbol} ({self.id[:3]})>"

    def summoned_pets(self, pet: "Pet") -> List["Pet"]:
        return []

    @abstractmethod
    def apply(self, player: "Player", pet: Optional["Pet"] = None) -> List["Pet"]:
        """
        Apply the food, and return which pets were affected
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def spawn(cls):
        raise NotImplementedError


class EatableFood(Food, ABC):
    power: int = 0
    toughness: int = 0

    def feed(self, pet: "Pet"):
        pet.buff(power=self.power, toughness=self.toughness)


class SingleEatableFood(EatableFood, ABC):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        self.feed(pet)
        return [pet]


@dataclass
class RandomEatableFood(EatableFood, ABC):
    targets: int = 0

    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        pets = pick_unique_pets(player.pets, self.targets)
        for pet in pets:
            self.feed(pet)
        return pets


class EquipableFood(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        if pet is None:
            assert ValueError("Can't apply food to None pet")
        pet.equipped_food = self
        return [pet]

    def enhance_attack(self, pet: "Pet", other_team: List["Pet"], damage_trigger: Trigger) -> List[Trigger]:
        return [damage_trigger]

    def reduce_damage(self, pet: Optional["Pet"], damage: int) -> int:
        return damage


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
    id: str = field(default_factory=lambda: Pet.generate_id())
    temp_buff_power: int = 0
    temp_buff_toughness: int = 0
    equipped_food: Optional[EquipableFood] = None

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def __repr__(self):
        food_str = str(self.equipped_food) if self.equipped_food else ""
        return f"<{self.symbol}{food_str}: {self.power} / {self.toughness}  ({self.id[:3]})>"

    def combine(self, other: "Pet"):
        if other.symbol != self.symbol:
            raise ValueError("Tried to merge different pet", self, other)
        self.power = max(self.power, other.power) + 1
        self.toughness = max(self.toughness, other.toughness) + 1
        self.experience += other.experience
        if other.equipped_food:
            self.equipped_food = other.equipped_food

    def add_experience(self, experience: int):
        self.buff(power=experience, toughness=experience)
        self.experience += experience

    def take_damage(self, damage: int) -> int:
        """Have the pet take damage, considering e.g. food, and return the damage actually taken"""
        damage = self.equipped_food.reduce_damage(self, damage) if self.equipped_food else damage
        self.toughness -= damage
        return damage

    def buff(self, power: int = 0, toughness: int = 0):
        self.power = min(self.power + power, MAX_POWER)
        self.toughness = min(self.toughness + toughness, MAX_TOUGHNESS)

    def temp_buff(self, power: int = 0, toughness: int = 0):
        # the temp buff is to keep track of what's temporary or not. We'll get rid of this after the round
        self.temp_buff_power += power
        self.temp_buff_toughness += toughness
        self.power += power
        self.toughness += toughness

    # TODO: remove this and replace with a trigger. Or the other way around? Probably other way around.
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

        if self not in my_team:
            # Pet has been removed already, so it can't trigger anything!
            return []

        # Handle tiger
        triggers = []
        if trigger.type == TriggerType.FORWARD_TRIGGER:
            actual_experience = self.experience
            self.experience = trigger.trigger_experience
            forwarded_trigger = trigger.forwarded_trigger
            triggers = self.apply_trigger(forwarded_trigger, my_team, other_team)
            self.experience = actual_experience
            return triggers  # don't run anything else, we want to run this as if the pet is a different level

        # Do this before faint triggers, so we can e.g. summon without removing
        triggers.extend(self._resolve_trigger(trigger, my_team, other_team))

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
                summoned_pets.extend(self.equipped_food.summoned_pets(self))

            if summoned_pets:
                triggers.append(Trigger(TriggerType.SUMMON_PET, self, summoned_pets=summoned_pets))

            # Do this last so the pet exists to be summoned off of
            triggers.append(Trigger(TriggerType.REMOVE_PET, self))

        return triggers

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        return []

    def attack(self, other_team: List["Pet"]) -> List[Trigger]:
        """
        Take the pet, and attack the other team. This generates events that can then be resolved.
        """
        damage_trigger = Trigger(TriggerType.DEAL_DAMAGE, other_team[0], damage=self.power)
        triggers = [damage_trigger]
        if self.equipped_food:
            triggers = self.equipped_food.enhance_attack(self, other_team, damage_trigger)

        return triggers


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
