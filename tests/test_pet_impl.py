from test_helpers import DummyPlayer, dummy_pet, StubShopGenerator
from sap.pet_impl import *
from sap.shop import Shop


class TestPetImpl:
    def test_rabbit(self):
        pets = [dummy_pet(toughness=1, power=1), Rabbit.spawn()]
        player = DummyPlayer(pets=pets)
        player._apply_food(Apple.spawn(), 0)
        assert pets[0].toughness == 3
        assert pets[0].power == 2

    def test_squirrel(self):
        pets = [Squirrel.spawn()]
        food = [Apple.spawn()]
        player = DummyPlayer(pets=pets, shop=Shop(StubShopGenerator(food=food)))
        player.start_turn(1)
        assert player.shop.food[0].food.cost == 2

    def test_worm(self):
        pets = [Worm.spawn()]
        player = DummyPlayer(pets=pets)
        player._apply_food(Apple.spawn(), 0)
        assert pets[0].toughness == 4
        assert pets[0].power == 4

    def test_cow(self):
        player = DummyPlayer(shop=Shop(StubShopGenerator(pets=[Cow.spawn() for _ in range(3)])))
        player.start_turn(1)
        player.buy_and_place_pet(0, 0)
        assert type(player.shop.food[0].food) == Milk
        assert type(player.shop.food[1].food) == Milk

    def test_seal(self):
        pets = [Seal.spawn(), dummy_pet(toughness=1, power=1), dummy_pet(toughness=1, power=1)]
        player = DummyPlayer(pets=pets)
        player._apply_food(Apple.spawn(), 0)
        assert pets[1].toughness == 2
        assert pets[2].toughness == 2
        assert pets[1].power == 2
        assert pets[2].power == 2
