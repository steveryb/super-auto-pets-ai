import gym
from gym import spaces
from enum import Enum
from typing import Optional, Dict, Union, TypeVar, List, Tuple, Callable

import sap.game
import sap.player as player
import sap.shop as shop
import sap.pet_impl as pet_impl
import sap.pet as pet
import sap.game as game
import random
import sap.battle as battle

import numpy as np


class Action(Enum):
    REROLL = 0
    BUY_AND_PLACE_PET = 1
    BUY_AND_COMBINE_PET = 2
    BUY_FOOD_FOR_PET = 3
    TOGGLE_FREEZE_PET = 4
    TOGGLE_FREEZE_FOOD = 5
    END_TURN = 6

    @staticmethod
    def get_action(val: int):
        for action in Action:
            if action.value == val:
                return action
        raise ValueError("Could not find action for value", val)


class EnvironmentPlayer(sap.player.Player):
    def buy_phase(self):
        """Do nothing, do this in the actual algo"""
        pass


T = TypeVar("T")
O = TypeVar("O")


def observation_list(l: List[T],
                     empty_gen: Callable[[], O],
                     mapper: Callable[[Union[T, Optional[T]]], O],
                     size: int) -> np.ndarray:
    return np.array([mapper(elem) for elem in l] + [empty_gen() for _ in range(size - len(l))])


def food_space():
    return spaces.Dict({
        'id': spaces.Discrete(len(pet_impl.ID_TO_FOOD_INFO)),
        'power': spaces.Discrete(pet.MAX_POWER + 1),
        'toughness': spaces.Discrete(pet.MAX_TOUGHNESS + 1),
    })


def empty_food_observation() -> Dict[str, int]:
    return {'id': 0, 'power': 0, 'toughness': 0}


def food_observation(food: Optional[pet.Food]) -> Dict[str, int]:
    if food is None:
        return empty_food_observation()
    return {
        'id': pet_impl.FOOD_TYPE_TO_ID[type(food)],
        'power': food.power,
        'toughness': food.toughness
    }


def pet_space():
    return spaces.Dict({
        'id': spaces.Discrete(len(pet_impl.ID_TO_PET_INFO)),
        # 'power': spaces.Discrete(pet.MAX_POWER + 1),
        # 'toughness': spaces.Discrete(pet.MAX_TOUGHNESS + 1),
        # 'temp_buff_power': spaces.Discrete(pet.MAX_POWER + 1),
        # 'temp_buff_tougness': spaces.Discrete(pet.MAX_TOUGHNESS + 1),
        # 'equipped_food': food_space(),
    })


def pet_observation(observed_pet: pet.Pet) -> Dict[str, Union[int, Dict[str, int]]]:
    return {
        'id': pet_impl.PET_TYPE_TO_ID[type(observed_pet)],
        # 'power': observed_pet.power,
        # 'toughness': observed_pet.toughness,
        # 'temp_buff_power': observed_pet.temp_buff_power,
        # 'temp_buff_toughness': observed_pet.temp_buff_toughness,
        # 'equipped_food': food_observation(observed_pet.equipped_food)
    }


def empty_pet_observation() -> Dict[str, Union[int, Dict[str, int]]]:
    return {
        'id': 0,
        # 'power': 0,
        # 'toughness': 0,
        # 'temp_buff_power': 0,
        # 'temp_buff_toughness': 0,
        # 'equipped_food': empty_food_observation()
    }


def player_space() -> spaces.Space:
    return spaces.Dict({
        'pets': spaces.Tuple(tuple(pet_space() for _ in range(player.MAX_PETS))),
        'gold': spaces.Discrete(100),
        'lives': spaces.Discrete(100),
        'wins': spaces.Discrete(10),
        'won_last': spaces.Discrete(2),
        'shop_food': spaces.Tuple((food_space(), food_space())),
        'shop_frozen_food':spaces.MultiBinary(shop.MAX_FOOD),
        'shop_pets':spaces.Tuple(tuple(pet_space() for _ in range(shop.MAX_PETS))),
        'shop_frozen_pets':spaces.MultiBinary(shop.MAX_PETS),
    })


def player_observation(observed_player: player.Player):
    observed_shop = observed_player.shop
    return {
        'pets': observation_list(observed_player.pets, empty_pet_observation, pet_observation, player.MAX_PETS),
        'gold': observed_player.gold,
        'lives': observed_player.lives,
        'wins': observed_player.wins,
        'won_last': 1 if observed_player.won_last else 0,
        'shop_food': observation_list(observed_shop.food, empty_food_observation,
                                 lambda item: food_observation(item.food), shop.MAX_FOOD),
        'shop_frozen_food': observation_list(observed_shop.food, lambda: False, lambda item: item.frozen, shop.MAX_FOOD),
        'shop_pets': observation_list(observed_shop.pets, empty_pet_observation, lambda item: pet_observation(item.pet),
                                 shop.MAX_PETS),
        'shop_frozen_pets': observation_list(observed_shop.pets, lambda: False, lambda item: item.frozen, shop.MAX_PETS),
    }


class SapRandomVersusEnv0(gym.Env):
    """Custom environment for having Super Auto Pets run in RL"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(SapRandomVersusEnv0, self).__init__()
        self.action_space = spaces.MultiDiscrete((
            len(Action),  # action value
            max(shop.MAX_PETS, shop.MAX_FOOD),  # index in shop
            player.MAX_PETS,  # index of pet on my team
        ))

        self.observation_space = player_space()
        self.game: Optional[sap.game.Game] = None

    def step(self, action: Tuple[int, int, int]):
        reward = 0

        action_enum: Action = Action.get_action(val=action[0])

        p1 = self.game.player_1
        shop_index = action[1]
        pet_index = action[2]
        try:
            if action_enum is Action.REROLL:
                p1.reroll()
            elif action_enum is Action.BUY_AND_PLACE_PET:
                p1.buy_and_place_pet(shop_index, pet_index)
            elif action_enum is Action.BUY_AND_COMBINE_PET:
                p1.buy_and_combine_pet(shop_index, pet_index)
            elif action_enum is Action.BUY_FOOD_FOR_PET:
                p1.buy_and_apply_food(shop_index, pet_index)
            elif action_enum is Action.TOGGLE_FREEZE_PET:
                p1.shop.toggle_freeze_pet(shop_index)
            elif action_enum is Action.TOGGLE_FREEZE_FOOD:
                p1.shop.toggle_freeze_food(shop_index)
            elif action_enum is Action.END_TURN:
                p1.end_turn()
                result = self.game.play_round()
                if result is battle.Result.TEAM_1_WINS:
                    # TODO: make this the number of points instead, but this works for now
                    reward = self.game.player_1.wins
                if result is battle.Result.TEAM_2_WINS:
                    reward = -3
        except (ValueError, IndexError):
            pass  # ignore invalid actions

        done = not self.game.player_1.has_lives()
        info = {"Player 1": player_observation(self.game.player_1), "Player 2": player_observation(self.game.player_2)}
        observation = player_observation(self.game.player_1)
        return observation, reward, done, info

    def reset(self):
        self.game = sap.game.Game(
            EnvironmentPlayer(name="Environment Player", shop=sap.game.create_shop()),
            sap.game.create_random_player()
        )

        return player_observation(self.game.player_1)

    def render(self, mode='human'):
        print(self.game.player_1, self.game.player_2)

    def close(self):
        pass

if __name__ == "__main__":
    from stable_baselines3.common.env_checker import check_env
    env = SapRandomVersusEnv0()
    print(player_space())
    print(env.reset())
    check_env(env)