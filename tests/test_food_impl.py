from sap.pet_impl import *
from sap.shop import Shop
from test_helpers import DummyPlayer, dummy_pet, StubShopGenerator


class TestFoodImpl:
    def apply_food(self, food, pet=None, player=None) -> Tuple[Player, Pet]:
        if player is None:
            player = DummyPlayer()
        if pet is None:
            pet = dummy_pet(power=1, toughness=1)
        player.place_pet(pet, 0)
        food.apply(player, pet)
        return player, pet

    def test_sleeping_pill(self):
        player, _ = self.apply_food(SleepingPill.spawn())
        assert player.pets == []

    def test_garlic(self):
        _, pet = self.apply_food(Garlic.spawn(), pet=dummy_pet(power=1, toughness=5))
        pet.take_damage(1)
        assert pet.toughness == 4
        pet.take_damage(2)
        assert pet.toughness == 3
        pet.take_damage(3)
        assert pet.toughness == 2
        pet.take_damage(4)
        assert pet.toughness == 0

    def test_salad_bowl(self):
        _, pet = self.apply_food(SaladBowl.spawn())
        assert pet.power == 2
        assert pet.toughness == 2

    def test_canned_food(self):
        player, _ = self.apply_food(
            player=DummyPlayer(shop=Shop(StubShopGenerator([dummy_pet(power=1, toughness=1) for _ in range(6)]))),
            food=CannedFood.spawn())

        player.start_turn(1)
        for shop_pet in player.shop.pets:
            assert shop_pet.pet.toughness == 2
            assert shop_pet.pet.power == 3

        player.reroll()

        for shop_pet in player.shop.pets:
            assert shop_pet.pet.toughness == 2
            assert shop_pet.pet.power == 3

    def test_chocolate(self):
        player = DummyPlayer(pets=[Fish.spawn(), Fish.spawn()])
        Chocolate.spawn().apply(player, player.pets[0])
        Chocolate.spawn().apply(player, player.pets[0])
        assert player.pets[0].experience == 2
        assert player.pets[0].toughness == 3 + 2
        assert player.pets[1].toughness == 3 + 1