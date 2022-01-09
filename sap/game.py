import logging
from random import Random
from typing import List, Tuple

from sap.battle import Battle, Result
from sap.pet import Pet
from sap.pet_impl import PET_TIERS, FOOD_TIERS
from sap.player import Player, RandomPlayer
from sap.shop import Shop, TierShopGenerator


class Game:
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.round = 0

    def buy_phase(self) -> Tuple[List[Pet], List[Pet]]:
        self.player_1.perform_buys(self.round)
        self.player_2.perform_buys(self.round)
        return self.player_1.pets, self.player_2.pets

    def battle_phase(self) -> Result:
        result = Battle(self.player_1.pets, self.player_2.pets).battle()
        if result == Result.TEAM_1_WINS:
            self.player_1.trigger_win()
            self.player_2.trigger_loss(self.round)
        elif result == Result.TEAM_2_WINS:
            self.player_1.trigger_loss(self.round)
            self.player_2.trigger_win()
        elif result == Result.DRAW:
            self.player_1.trigger_draw()
            self.player_2.trigger_draw()
        else:
            raise ValueError("Unexpected result", result)

        return result

    def start_round(self):
        self.round += 1
        logging.info(f"Starting round {self.round}")

    def play_round(self) -> Result:
        self.start_round()
        self.buy_phase()
        logging.info(f"Battle between {self.player_1} and {self.player_2}")
        result = self.battle_phase()
        logging.info(f"Result: {result}")
        return result

    def play_game(self) -> Result:
        last_result = Result.UNFINISHED
        while self.player_1.has_lives() and self.player_2.has_lives():
            last_result = self.play_round()
        logging.info(f"Final result: {last_result}")
        return last_result


def create_shop():
    return Shop(TierShopGenerator(PET_TIERS, FOOD_TIERS))


def create_random_player():
    return RandomPlayer(create_shop(), Random())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    random_gen = Random()
    shop_generator = TierShopGenerator(PET_TIERS, FOOD_TIERS)
    for i in range(1):
        game = Game(
            # RealPlayer(Shop(shop_generator)),
            create_random_player(),
            create_random_player()
        )
        game.play_game()
