from sap.pet import Pet
from sap.shop import ShopGenerator, Shop
from sap.player import Player
from copy import deepcopy

from typing import List, Sequence, TypeVar
from random import Random


def dummy_pet(symbol="T", power=1, toughness=2, experience=0):
    return Pet(symbol=symbol, power=power, toughness=toughness, experience=experience)


def create_pets(num: int):
    return [
        Pet(
            name=str(i),
            symbol=str(i),
            toughness=i,
            power=i * 2
        ) for i in range(1, num + 1)
    ]


class StubShopGenerator(ShopGenerator):
    def __init__(self, pets: List[Pet]):
        self.pets = deepcopy(pets)

    def get_pet(self) -> Pet:
        assert len(self.pets) > 0
        return self.pets.pop(0)


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
    def __init__(self, pets: List[Pet] = None):
        super().__init__("Dummy Player", pets)

    def buy_phase(self, shop: Shop):
        pass
