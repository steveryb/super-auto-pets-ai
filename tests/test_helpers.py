from sap.pet import Pet, Food
from sap.shop import ShopGenerator, Shop, TierShopGenerator
from sap.player import Player
from copy import deepcopy
from sap.pet_impl import PET_TIERS, FOOD_TIERS, Apple

from typing import List, Sequence, TypeVar, Optional
from random import Random


def dummy_pet(symbol="T", power=1, toughness=2, experience=0):
    return Pet(symbol=symbol, power=power, toughness=toughness, experience=experience)


def create_pets(num: int):
    return [
        Pet(
            symbol=str(i),
            toughness=i,
            power=i * 2
        ) for i in range(1, num + 1)
    ]


class StubShopGenerator(ShopGenerator):
    def __init__(self, pets: Optional[List[Pet]] = None, food: Optional[List[Food]] = None, random_gen: Random=Random()):
        """"""
        super().__init__(random_gen)

        self.pets = deepcopy(pets)
        self.food = deepcopy(food)

    def get_pet(self, tier: int) -> Pet:
        if self.pets is None:
            return dummy_pet()
        return self.pets.pop(0)

    def get_food(self, tier: int) -> Food:
        if self.food is None:
            return Apple.spawn()
        return self.food.pop(0)


def create_shop(num: int) -> Shop:
    return Shop(shop_generator=StubShopGenerator(create_pets(num)))


_T = TypeVar("_T")


# TODO: this ends up being really hacky, it'd be better if we had our own random with custom methods
class TestRandom(Random):
    def __init__(self):
        super().__init__()
        self.choices = []

    def choice(self, seq: Sequence[_T]) -> _T:
        return self.choices.pop(0)


class DummyPlayer(Player):
    def __init__(self, shop: Shop = None, pets: List[Pet] = None):
        if shop is None:
            shop = Shop(TierShopGenerator(PET_TIERS, FOOD_TIERS))
        super().__init__("Dummy Player", shop=shop, pets=pets)

    def buy_phase(self):
        pass
