from sap.pet_impl import *
from sap.battle import Battle
from test_helpers import dummy_pet, TestRandom, DummyPlayer


class TestPetImplBattle:
    def test_solo_mosquito(self):
        b = Battle(
            [Mosquito.spawn()], [dummy_pet(toughness=1)]
        )
        b.battle()
        assert len(b.team_1) == 1
        assert b.team_2 == []

    def test_flamingo(self):
        b = Battle(
            [Flamingo.spawn(), Pet.spawn(), Pet.spawn()], [Pet.spawn()]
        )
        b.battle()
        team = b.team_1
        assert team[0].power, b.team_1[0].toughness == (2, 2)
        assert team[1].power, b.team_1[1].toughness == (2, 2)

    def test_hedgehog(self):
        last_pet_standing = Pet(power=1, toughness=3, symbol="T")
        b = Battle(
            [Hedgehog.spawn(), Pet.spawn()],
            [Pet.spawn(), Pet.spawn(), Pet.spawn(), Pet.spawn(), last_pet_standing]
        )
        b.battle()
        last_pet_standing.take_damage(2)
        assert b.team_1 == []
        assert b.team_2 == [last_pet_standing]

    def test_double_hedgehog_with_summons(self):
        b = Battle(
            [Hedgehog.spawn()],
            [Hedgehog.spawn(), Cricket.spawn()]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert type(b.team_2[0]) == ZombieCricket

    def test_hedgehog_badger_summons(self):
        b = Battle(
            [Dodo.spawn(), Cricket.spawn(), Hedgehog.spawn()],
            [Hedgehog.spawn(), Cricket.spawn()],
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_hedgehog_flamingo(self):
        b = Battle(
            [Pet(power=2, toughness=1, symbol="P"), Flamingo.spawn(), Hedgehog.spawn(), Cricket.spawn()],
            [Hedgehog.spawn()]
        )
        b.battle()
        assert b.team_2 == []
        assert len(b.team_1) == 1
        assert type(b.team_1[0]) == ZombieCricket
        assert b.team_1[0].power, b.team_1[0].toughness == (1, 1)

    def test_peacock(self):
        b = Battle(
            [Peacock.spawn()],
            [dummy_pet(toughness=1), dummy_pet(toughness=3), dummy_pet(toughness=5), dummy_pet(toughness=7),
             dummy_pet(toughness=9)]
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_rat(self):
        b = Battle(
            [Rat.spawn(), dummy_pet(power=1, toughness=1), dummy_pet(power=1, toughness=1)],
            [dummy_pet(power=5, toughness=6)]
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_dog(self):
        r = TestRandom()
        r.choices = [True, True]

        b = Battle(
            [Cricket.spawn(), Cricket.spawn(), Dog(symbol="D", power=2, toughness=2, random_gen=r)],
            [dummy_pet(power=10, toughness=8)]
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_spider(self):
        r = TestRandom()
        r.choices = [Dog]
        spider = Spider(power=2, toughness=2, symbol="S", random_gen=r)

        b = Battle(
            [spider],
            [dummy_pet(power=2, toughness=4)]
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_badger_hedgehog_clusterfuck(self):
        b = Battle(
            [Hedgehog.spawn(), Hedgehog.spawn(), dummy_pet(toughness=9), Badger.spawn(), dummy_pet(toughness=9)],
            [dummy_pet(power=2, toughness=8)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_badger_other_team(self):
        b = Battle(
            [Badger.spawn(), dummy_pet(toughness=5)],
            [dummy_pet(power=4, toughness=11)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_badger(self):
        b = Battle(
            [Badger.spawn(), dummy_pet(toughness=5)],
            [dummy_pet(power=4, toughness=1), dummy_pet(toughness=6)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_blowfish(self):
        b = Battle(
            [Hedgehog.spawn(), Blowfish(power=3, toughness=7, symbol="Blowfish")],
            [dummy_pet(power=3, toughness=16)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_camel(self):
        b = Battle(
            [Camel.spawn(), dummy_pet(power=1, toughness=1)],
            [dummy_pet(power=1, toughness=56)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_giraffe(self):
        giraffe = Giraffe.spawn()
        team_1 = [dummy_pet(power=1, toughness=1), giraffe]
        team_2 = [dummy_pet(power=5, toughness=5)]
        giraffe.apply_trigger(Trigger(TriggerType.TURN_ENDED), team_1, team_2)

        b = Battle(
            team_1,
            team_2
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_kangaroo(self):
        b = Battle(

            [Cricket.spawn(), Kangaroo.spawn()],
            [dummy_pet(power=6, toughness=8)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_sheep(self):
        b = Battle(
            [Sheep.spawn(), Sheep.spawn(),
             dummy_pet(power=1, toughness=1), dummy_pet(power=1, toughness=1), dummy_pet(power=1, toughness=1)],
            [dummy_pet(power=2, toughness=2 * 2 + 2 * 3 + 1 * 3 + 1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_snail_lost(self):
        player = DummyPlayer()
        player.won_last = False
        snail = Snail.spawn()
        team_1 = [snail, dummy_pet(power=1, toughness=1)]
        team_2 = [dummy_pet(power=2, toughness=6)]
        snail.apply_trigger(Trigger(TriggerType.PET_BOUGHT, snail, player=player), team_1, team_2)

        b = Battle(team_1, team_2)
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_snail_won(self):
        player = DummyPlayer()
        player.won_last = True
        snail = Snail.spawn()
        team_1 = [snail, dummy_pet(power=1, toughness=1)]
        team_2 = [dummy_pet(power=2, toughness=4)]
        snail.apply_trigger(Trigger(TriggerType.PET_BOUGHT, snail, player=player), team_1, team_2)

        b = Battle(team_1, team_2)
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_whale(self):
        whale = Whale.spawn()
        whale.experience = 3  # level 2
        b = Battle(
            [Sheep.spawn(), whale],
            [dummy_pet(power=6, toughness=2 * 2 + 2 + 3 * 4 + 1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_bison(self):
        bison = Bison.spawn()
        team_1 = [dummy_pet(power=1, toughness=1, experience=6), bison]
        team_2 = [dummy_pet(power=8, toughness=10)]
        bison.apply_trigger(Trigger(TriggerType.TURN_ENDED), team_1, team_2)

        b = Battle(
            team_1,
            team_2
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_dolphin(self):
        b = Battle(
            [Dolphin.spawn()],
            [dummy_pet(power=6, toughness=6), dummy_pet(power=100, toughness=5)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 2

    def test_hippo(self):
        b = Battle(
            [Hippo.spawn()],
            [Cricket.spawn(), dummy_pet(power=6, toughness=9)]
        )
        b.battle()
        print(b)
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_penguin(self):
        penguin = Penguin.spawn()
        team_1 = [dummy_pet(power=1, toughness=1, experience=7), penguin]
        team_2 = [dummy_pet(power=2, toughness=4)]
        penguin.apply_trigger(Trigger(TriggerType.TURN_ENDED), team_1, team_2)

        b = Battle(
            team_1,
            team_2
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_rooster(self):
        b = Battle(
            [Rooster.spawn()],
            [dummy_pet(power=3, toughness=8)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_skunk(self):
        b = Battle(
            [Skunk(symbol="S", power=3, toughness=6, experience=7)],
            [dummy_pet(power=100, toughness=100), dummy_pet(power=6, toughness=4)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_monkey(self):
        monkey = Monkey.spawn()
        team_1 = [dummy_pet(power=1, toughness=1), monkey]
        team_2 = [dummy_pet(power=4, toughness=6)]
        monkey.apply_trigger(Trigger(TriggerType.TURN_ENDED), team_1, team_2)

        b = Battle(
            team_1,
            team_2
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_crocodile(self):
        b = Battle(
            [Crocodile.spawn()],
            [dummy_pet(power=4, toughness=9), dummy_pet(power=100, toughness=8)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_rhino(self):
        b = Battle(
            [Rhino.spawn()],
            [Cricket.spawn(), Rooster.spawn(), dummy_pet(power=7, toughness=9), dummy_pet(power=1, toughness=1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_shark(self):
        b = Battle(
            [Cricket.spawn(), Shark.spawn()],
            [dummy_pet(toughness=1 + 1 + 8 + 1, power=6)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_turkey(self):
        b = Battle(
            [Cricket.spawn(), Turkey.spawn()],
            [dummy_pet(toughness=1 + 4 + 3 + 1, power=4)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_boar(self):
        b = Battle(
            [Boar.spawn()],
            [Cricket.spawn(), dummy_pet(toughness=15, power=10)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_dragon(self):
        dragon = Dragon.spawn()
        team_1 = [Cricket.spawn(), dragon]
        team_2 = [dummy_pet(toughness=2 + 1 + 7 + 1, power=9)]
        dragon.apply_trigger(Trigger(TriggerType.PET_BOUGHT, team_1[0]), team_1, team_2)
        b = Battle(team_1, team_2)
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_fly(self):
        b = Battle(
            [Cricket.spawn(), Cricket.spawn(), Fly.spawn()],
            [dummy_pet(toughness=1 + 5 + 1 + 5 + 1 + 5 + 1 + 5 + 1, power=5)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_leopard(self):
        b = Battle(
            [Leopard.spawn()],
            [dummy_pet(toughness=16, power=4)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_mammoth(self):
        b = Battle(
            [Mammoth.spawn(), Cricket.spawn()],
            [dummy_pet(toughness=3 + 3 + 1 + 1, power=10)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_snake(self):
        b = Battle(
            [dummy_pet(toughness=1, power=1), dummy_pet(toughness=1, power=1), Snake.spawn()],
            [dummy_pet(power=6, toughness=1 + 1 + 5 + 6 + 1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_tiger(self):
        b = Battle(
            [dummy_pet(1, 1), Snake.spawn(), Tiger.spawn()],
            [dummy_pet(power=6, toughness=1 + 5 + 5 + 6 + 4 + 1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_honey(self):
        b = Battle(
            [Pet(symbol="P", power=1, toughness=1, equipped_food=Honey.spawn())],
            [dummy_pet(power=1, toughness=3)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_meat_bone(self):
        b = Battle(
            [Pet(symbol="P", power=1, toughness=1, equipped_food=MeatBone.spawn())],
            [dummy_pet(power=1, toughness=7)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_chilli(self):
        b = Battle(
            [Pet(symbol="P", power=1, toughness=1, equipped_food=Chili.spawn())],
            [dummy_pet(power=1, toughness=2), dummy_pet(power=100, toughness=5)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_melon(self):
        b = Battle(
            [Pet(symbol="P", power=1, toughness=2, equipped_food=Melon.spawn())],
            [dummy_pet(power=21, toughness=1), dummy_pet(power=2, toughness=2)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_mushroom(self):
        cricket = Cricket.spawn()
        cricket.equipped_food = Mushroom.spawn()
        b = Battle(
            [cricket],
            [dummy_pet(power=2, toughness=1+1+1+1+1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_ox(self):
        b = Battle(
            [Cricket.spawn(), Ox.spawn()],
            [dummy_pet(power=20, toughness=1+1+5+5+1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_turtle(self):
        b = Battle(
            [Turtle.spawn(), dummy_pet(power=1, toughness=1)],
            [dummy_pet(power=20, toughness=1+1+1+1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1

    def test_deer(self):
        b = Battle(
            [Deer.spawn()],
            [dummy_pet(toughness=2, power=5),dummy_pet(power=100, toughness=5), dummy_pet(power=100, toughness=1)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1
        # TODO: test tiger whale

    def test_scorpion(self):
        b = Battle(
            [Scorpion.spawn(), Scorpion.spawn(), Scorpion.spawn()],
            [Pet(symbol="P", toughness=100, power=100, equipped_food=Garlic.spawn()), # garlic reduces to 1, so dies
             Pet(symbol="P", toughness=100, power=100, equipped_food=Melon.spawn()) # should take a hit though
             ]
        )
        b.battle()
        assert b.team_1 == []
        assert b.team_2 == []

    def test_gorilla(self):
        b = Battle(
            [Gorilla.spawn()],
            [dummy_pet(power=8, toughness=6), dummy_pet(power=100, toughness=6), dummy_pet(power=1, toughness=7)]
        )
        b.battle()
        assert b.team_1 == []
        assert len(b.team_2) == 1
        assert b.team_2[0].toughness == 1
