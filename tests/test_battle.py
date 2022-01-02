from typing import List
from test_helpers import create_pets, dummy_pet
from sap.battle import *


class TestBattle:
    def test_assess_empty(self):
        assert Battle([], []).assess() == Result.DRAW

    def test_assess_team_1_wins(self):
        assert Battle([dummy_pet()], []).assess() == Result.TEAM_1_WINS

    def test_assess_team_2_wins(self):
        assert Battle([], [dummy_pet()]).assess() == Result.TEAM_2_WINS

    def test_assess_unfinished(self):
        assert Battle([dummy_pet()], [dummy_pet()]).assess() == Result.UNFINISHED

    def test_do_round_empty(self):
        assert Battle([], []).do_round() == ([], [])

    def test_do_round_equal(self):
        assert Battle([dummy_pet(power=1, toughness=1)],
                      [dummy_pet(power=1, toughness=1)]).do_round() == ([], [])

    def test_do_round_bigger(self):
        assert Battle([dummy_pet(power=1, toughness=1)],
                      [dummy_pet(power=2, toughness=2)]).do_round() == \
               ([], [dummy_pet(power=2, toughness=1)])

    def test_do_round_move_next_up(self):
        assert Battle([dummy_pet(power=1, toughness=1), dummy_pet(power=1, toughness=1)],
                      [dummy_pet(power=2, toughness=2)]).do_round() == \
               ([dummy_pet(power=1, toughness=1)],
                [dummy_pet(power=2, toughness=1)])

    def test_do_run_only_damaged(self):
        assert Battle([dummy_pet(power=8, toughness=3)],
                      [dummy_pet(power=2, toughness=10)]).do_round() == \
               ([dummy_pet(power=8, toughness=1)],
                [dummy_pet(power=2, toughness=2)])

    def test_battle(self):
        assert Battle([
            dummy_pet(power=1, toughness=1),
            dummy_pet(power=2, toughness=2),
            dummy_pet(power=3, toughness=3),
            dummy_pet(power=4, toughness=4),
            dummy_pet(power=5, toughness=5),
        ], [
            dummy_pet(power=3, toughness=6),
            dummy_pet(power=4, toughness=5)
        ]).battle() == Result.TEAM_1_WINS
