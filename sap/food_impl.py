from sap.pet import Pet, Food, EquipableFood, Trigger, TriggerType, pick_unique_pets
from sap.player import Player
from typing import Tuple, Type, List, Optional
from abc import ABC, abstractmethod
from sap.pet_impl import Bee


class Apple(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        pet.buff(power=1, toughness=1)


class Cupcake(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        pet.temp_buff(power=3, toughness=3)


class Honey(EquipableFood):
    def summoned_pets(self) -> List["Pet"]:
        return [Bee.create()]


class MeatBone(EquipableFood):
    def attack_bonus(self) -> int:
        return 5


class SleepingPill(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        player.apply_trigger(Trigger(TriggerType.FAINT_PET, pet))


class Garlic(EquipableFood):
    def reduce_damage(self, damage: int) -> int:
        return max(1, damage - 2)  # always take at least one damage, sadly

class SaladBowl(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        for pet in pick_unique_pets(player.pets, 2, random_gen=self.random_gen):
            pet.buff(power=1, toughness=1)

class Pear(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        pet.buff(power=2, toughness=2)

class CannedFood(Food):
    def apply(self, player: "Player", pet: Optional["Pet"] = None):
       pass


FOOD_TIERS: Tuple[Tuple[Type[Food], ...], ...] = (
    (Apple, Honey),
    (Cupcake, MeatBone, SleepingPill),
    (Garlic, SaladBowl)
)
