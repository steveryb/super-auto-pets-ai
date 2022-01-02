from player import Player, RealPlayer, RandomPlayer
from shop import ShopGenerator, Shop, RandomShopGenerator, TierShopGenerator
from battle import Battle, Result
from random import Random
from pet import Pet
from pet_impl import PET_TIERS

from typing import List, Tuple, Optional
import logging

class Game:
    def __init__(self, shop_generator: ShopGenerator, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1_shop = Shop(shop_generator)
        self.player_2_shop = Shop(shop_generator)
        self.round = 0


    def buy_phase(self) -> Tuple[List[Pet], List[Pet]]:
        self.player_1.perform_buys(self.player_1_shop, self.round)
        self.player_2.perform_buys(self.player_2_shop, self.round)
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

    def play_round(self) -> Result:
        self.round += 1
        logging.info(f"Starting round {self.round}")
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    random_gen = Random()
    for i in range(1000):
        game = Game(
            TierShopGenerator(PET_TIERS),
            # RealPlayer(),
            RandomPlayer(random_gen),
            RandomPlayer(random_gen),
        )
        game.play_game()
