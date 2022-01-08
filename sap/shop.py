import random

from sap.pet import Pet, Food
from typing import List, Tuple, Type, TypeVar
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random


class ShopGenerator(ABC):
    def __init__(self, random_gen: Random):
        self.random = random_gen

    @abstractmethod
    def get_pet(self, tier: int) -> Pet:
        raise NotImplementedError

    @abstractmethod
    def get_food(self, tier: int) -> Food:
        raise NotImplementedError


T = TypeVar("T")

MAX_PETS = 5
MAX_FOOD = 2
MAX_TIER = 6


class TierShopGenerator(ShopGenerator):
    def __init__(self, pet_tiers: List[List[Type[Pet]]], food_tiers: List[List[Type[Food]]],
                 random_gen: Random = random.Random()):
        super().__init__(random_gen)
        self.pet_tiers = pet_tiers
        self.food_tiers = food_tiers

    def get_from_tier(self, tier: int, tiers: List[List[Type[T]]]) -> Type[T]:
        available_tiers = tiers[:tier]
        available_items = tuple(item for tier in available_tiers for item in tier)
        return self.random.choice(available_items)

    def get_pet(self, tier: int) -> Pet:
        return self.get_from_tier(tier, self.pet_tiers).spawn()

    def get_food(self, tier: int) -> Food:
        return self.get_from_tier(tier, self.food_tiers).spawn()


@dataclass
class ShopPet:
    pet: Pet
    frozen: bool = False

    def __repr__(self) -> str:
        pet_string = str(self.pet)
        if self.frozen:
            pet_string = "🧊" + pet_string
        return pet_string


@dataclass
class ShopFood:
    food: Food
    frozen: bool = False

    def __repr__(self) -> str:
        food_string = str(self.food)
        if self.frozen:
            food_string = "🧊" + food_string
        return food_string


# TODO: deal with level up shop spawn
class Shop:
    def __init__(self, shop_generator: ShopGenerator):
        self.generator = shop_generator
        self._pets: List[ShopPet] = []
        self._food: List[ShopFood] = []
        self.round = 0  # needs to be setup
        self.power_buff = 0
        self.toughness_buff = 0

    @property
    def pet_size(self) -> int:
        if 0 <= self.round < 5:
            return 3
        if 5 <= self.round < 9:
            return 4
        return MAX_PETS

    @property
    def food_size(self) -> int:
        if 0 <= self.round < 3:
            return 1
        return MAX_FOOD

    @property
    def has_open_slot(self) -> bool:
        """
        Number of slots left for pets.

        As far as I can tell, you can think of the shop as having a maximum size of 6. Some slots are unlocked later,
        but can be used by pets generated by leveling until then. If you try to level up, and  there's no free slots,
        you don't get the pet.
        """
        return 6 - len(self.food) + len(self.pets) > 0

    @property
    def tier(self):
        return min(((self.round + 1) // 2), MAX_TIER)

    @property
    def pets(self) -> List[ShopPet]:
        return self._pets

    @property
    def food(self) -> List[ShopFood]:
        return self._food

    def buff(self, power: int = 0, toughness: int = 0):
        self.power_buff += power
        self.toughness_buff += toughness
        for shop_pet in self._pets:
            shop_pet.pet.buff(power=power, toughness=toughness)

    def add_next_tier_pet(self):
        """When leveling up, we get to add a new, better, pet!"""
        self.add_pet(ShopPet(pet=self.generator.get_pet(self.tier + 1)))

    def add_pet(self, shop_pet: ShopPet):
        if not self.has_open_slot:
            raise ValueError("Can't add a pet if there's no spot!")
        shop_pet.pet.buff(power=self.power_buff, toughness=self.toughness_buff)
        self._pets.append(shop_pet)

    def reroll(self):
        self._pets = [pet for pet in self._pets if pet.frozen]
        for _ in range(len(self._pets), self.pet_size):
            self.add_pet(ShopPet(pet=self.generator.get_pet(self.tier)))

        self._food = [food for food in self._food if food.frozen]
        for _ in range(len(self._food), self.food_size):
            self._food.append(ShopFood(food=self.generator.get_food(self.tier)))

    def buy_pet(self, position: int) -> Pet:
        return self._pets.pop(position).pet

    def buy_food(self, position: int) -> Food:
        return self._food.pop(position).food

    def replace_shop(self, foods: List[Food]):
        self._food = [ShopFood(food=food) for food in foods]

    def toggle_freeze_pet(self, position: int) -> bool:
        pet = self._pets[position]
        pet.frozen = not pet.frozen
        return pet.frozen

    def toggle_freeze_food(self, position: int) -> bool:
        food = self._food[position]
        food.frozen = not food.frozen
        return food.frozen

    def setup_for_round(self, game_round: int):
        self.round = game_round
        self.reroll()

    def __repr__(self):
        pet_illustration = [""]
        for i, pet in enumerate(self.pets):
            pet_illustration.append(f"{i}. {pet}")
        pets_string = "\n".join(pet_illustration)

        food_illustration = [""]
        for i, food in enumerate(self.food):
            food_illustration.append(f"{i}. {food}")
        foods_string = "\n".join(food_illustration)
        return f"<Shop {pets_string} {foods_string}>"
