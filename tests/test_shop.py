from sap.shop import *
from test_helpers import create_pets, StubShopGenerator
from typing import Optional

SHOP_SIZE = 5

class TestShop:
    def make_shop(self, pets: List[Pet], food: Optional[List[Food]] = None):
        shop = Shop(StubShopGenerator(pets, food))
        shop.setup_for_round(1)
        return shop

    def test_reroll(self):
        pets = create_pets(SHOP_SIZE * 2)
        shop = self.make_shop(pets, [])
        shop.reroll()
        assert shop.pets == pets[SHOP_SIZE:]

    def test_buy(self):
        pets = create_pets(SHOP_SIZE)
        shop = self.make_shop(pets, [])
        assert shop.buy_pet(1) == pets[1]
        assert shop.pets == pets[0:1] + pets[2:]

    def test_toggle_freeze(self):
        shop = self.make_shop(create_pets(SHOP_SIZE), [])
        assert shop.frozen[0] is False
        shop.toggle_freeze_pet(0)
        assert shop.frozen[0] is True
        shop.toggle_freeze_pet(0)
        assert shop.frozen[0] is False

    def test_freezing_saves_reroll(self):
        pets = create_pets(SHOP_SIZE * 2)
        shop = self.make_shop(pets)
        shop.toggle_freeze_pet(1)
        shop.reroll()
        assert shop.pets[0] == pets[SHOP_SIZE]
        assert shop.pets[1] == pets[1]
        assert shop.pets[2:] == pets[SHOP_SIZE+1:-1]


