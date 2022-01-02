import pytest
from sap.player import *
from test_helpers import create_shop, dummy_pet, create_pets




class TestPlayer:
    def test_place_pet_empty(self):
        pet = dummy_pet()
        player = DummyPlayer()
        assert player.place_pet(pet, 0) == [pet]

    def test_place_pet_non_empty(self):
        pet1 = dummy_pet("Test1")
        pet2 = dummy_pet("Test2")
        player = DummyPlayer([pet1])
        assert player.place_pet(pet2, 0) == [pet2, pet1]

    def test_place_full(self):
        player = DummyPlayer(create_pets(5))
        with pytest.raises(ValueError):
            player.place_pet(dummy_pet(), 0)

    def test_buy(self):
        player = DummyPlayer()
        player.start_turn()
        shop = create_shop(5, 5)
        pet_1 = shop.pets[1]
        assert player.buy(shop, 1, 0) == [pet_1]
        assert len(shop.pets) == 4

    def test_buy_no_gold(self):
        player = DummyPlayer()
        shop = create_shop(5, 5)
        with pytest.raises(ValueError):
            player.buy(shop, 1, 0)

    def test_condense(self):
        pet_1 = dummy_pet()
        pet_2 = dummy_pet()
        pets = [pet_1, None, None, pet_2, None]
        player = DummyPlayer(pets)
        assert player.condense() == [pet_1, pet_2]



