from sap.player import Player
from sap.food_impl import *
from test_helpers import DummyPlayer, dummy_pet

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
        player, pet = self.apply_food(SleepingPill())
        assert player.pets == []

    def test_garlic(self):
        player, pet = self.apply_food(Garlic(), pet=dummy_pet(power=1, toughness=5))
        pet.take_damage(1)
        assert pet.toughness == 4
        pet.take_damage(2)
        assert pet.toughness == 3
        pet.take_damage(3)
        assert pet.toughness == 2
        pet.take_damage(4)
        assert pet.toughness == 0

    def test_salad_bowl(self):
        player, pet = self.apply_food(SaladBowl())
        assert pet.power == 2
        assert pet.toughness == 2
