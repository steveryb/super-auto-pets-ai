from pet import Pet, Food, EquipableFood
from player import Player
from typing import Tuple, Type, List
from abc import ABC, abstractmethod
from pet_impl import Bee


class Apple(Food):
    def apply(self, pet: Pet, player: Player):
        pet.buff(power=1, toughness=1)


class Cupcake(Food):
    def apply(self, pet: Pet, player: Player):
        pet.temp_buff(power=3, toughness=3)


class Honey(EquipableFood):
    def summoned_pets(self) -> List["Pet"]:
        return [Bee.create()]


FOOD_TIERS: Tuple[Tuple[Type[Food], ...], ...] = (
    (Apple, Honey),
    (Cupcake,)
)
