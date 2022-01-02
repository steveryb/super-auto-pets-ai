import random

from sap.pet import Pet
from typing import List, Tuple, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random


class ShopGenerator(ABC):
    def __init__(self, random_gen: Random):
        self.random = random_gen

    @abstractmethod
    def get_pet(self, tier: int) -> Pet:
        raise NotImplementedError


class RandomShopGenerator(ShopGenerator):
    def get_pet(self, tier: int) -> Pet:
        return Pet(
            name="RP",
            symbol="🍟",
            power=random.randint(1, 10),
            toughness=random.randint(1, 10)
        )


class TierShopGenerator(ShopGenerator):
    def __init__(self, tiers: Tuple[Tuple[Type[Pet], ...], ...], random_gen: Random=random.Random()):
        super().__init__(random_gen)
        self.tiers = tiers

    def get_pet(self, tier: int) -> Pet:
        available_tiers = self.tiers[:tier]
        available_pets = tuple(pet for tier in available_tiers for pet in tier)
        return self.random.choice(available_pets).spawn()


@dataclass()
class ShopPet:
    pet: Pet
    frozen: bool = False

    def __repr__(self) -> str:
        pet_string = str(self.pet)
        if self.frozen:
            pet_string = "🧊" + pet_string
        return pet_string


class Shop:
    def __init__(self, shop_generator: ShopGenerator):
        self.generator = shop_generator
        self.size = -1  # needs to be setup
        self._pets: List[ShopPet] = []
        self.tier = 0

    def get_pet_size(self, round: int) -> int:
        if 0 <= round < 5:
            return 3
        if 5 <= round < 9:
            return 4
        return 5

    def _check_bounds(self, i: int):
        if i < 0 or i >= self.size:
            raise IndexError("Given index is not within bounds", i)

    @property
    def pets(self) -> List[ShopPet]:
        return self._pets

    def reroll(self):
        self._pets = [pet for pet in self._pets if pet.frozen]
        for _ in range(len(self._pets), self.size):
            self._pets.append(ShopPet(pet=self.generator.get_pet(self.tier)))

    def buy(self, position: int) -> Pet:
        self._check_bounds(position)
        return self._pets.pop(position).pet

    def toggle_freeze(self, position: int) -> bool:
        self._check_bounds(position)
        pet = self._pets[position]
        pet.frozen = not pet.frozen
        return pet.frozen

    def num_pets(self):
        # TODO: think about abstracting this
        return len([pet for pet in self.pets if pet is not None])

    def setup_for_round(self, game_round: int):
        self.size = self.get_pet_size(game_round)
        self.tier = min(((game_round + 1) // 2), 6)
        self.reroll()

    def __repr__(self):
        pet_illustration = [""]
        for i, pet in enumerate(self.pets):
            pet_illustration.append(f"{i}. {pet}")
        pets_string = "\n".join(pet_illustration)
        return f"<Shop {pets_string}>"
