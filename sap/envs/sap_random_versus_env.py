import os
from enum import Enum
from typing import Optional, Union, TypeVar, List, Tuple, Callable

import gym
import numpy as np
from gym import spaces

import sap.battle as battle
import sap.game as game
import sap.pet as pet
import sap.pet_impl as pet_impl
import sap.player as player
import sap.shop as shop


class Action(Enum):
    REROLL = 0
    BUY_AND_PLACE_PET = 1
    BUY_AND_COMBINE_PET = 2
    BUY_FOOD_FOR_PET = 3
    TOGGLE_FREEZE_PET = 4
    TOGGLE_FREEZE_FOOD = 5
    SELL_PET = 6
    MOVE_PET = 7
    END_TURN = 8

    @staticmethod
    def get_action(val: int):
        for action in Action:
            if action.value == val:
                return action
        raise ValueError("Could not find action for value", val)


class EnvironmentPlayer(player.Player):
    def __init__(self, given_shop: shop.Shop):
        super().__init__("Environment Player", given_shop)

    def buy_phase(self):
        """Do nothing, do this in the actual algo"""
        pass


T = TypeVar("T")
O = TypeVar("O")


def observation_list(l: List[T],
                     empty_gen: Callable[[], O],
                     mapper: Callable[[Union[T, Optional[T]]], O],
                     size: int) -> List[O]:
    return [mapper(elem) for elem in l] + [empty_gen() for _ in range(size - len(l))]


def food_space():
    return spaces.MultiDiscrete([
        len(pet_impl.ID_TO_FOOD_INFO),  # id
        pet.MAX_POWER + 1,  # power
        pet.MAX_TOUGHNESS + 1,  # toughness
    ])


def empty_food_observation() -> List[int]:
    return [
        0,  # id
        0,  # power
        0,  # toughness
    ]


def food_observation(food: Optional[pet.Food]) -> List[int]:
    if food is None:
        return empty_food_observation()
    return [
        pet_impl.FOOD_TYPE_TO_ID[type(food)],
        food.power,
        food.toughness
    ]


# TODO: consider changing this from ID to something that represents the pet?
def pet_space():
    return spaces.Tuple((
        spaces.Discrete(len(pet_impl.ID_TO_PET_INFO)),  # id
        spaces.Discrete(pet.MAX_POWER + 1),  # power
        spaces.Discrete(pet.MAX_TOUGHNESS + 1),  # toughness
        spaces.Discrete(pet.MAX_POWER + 1),  # temp_buff_power
        spaces.Discrete(pet.MAX_TOUGHNESS + 1),  # temp_buff_tougness
        food_space(),  # equipped_food
    ))


def pet_observation(observed_pet: pet.Pet) -> Tuple:
    return (
        pet_impl.PET_TYPE_TO_ID[type(observed_pet)],
        observed_pet.power,
        observed_pet.toughness,
        observed_pet.temp_buff_power,
        observed_pet.temp_buff_toughness,
        food_observation(observed_pet.equipped_food)
    )


def empty_pet_observation() -> Tuple:
    return (
        0,  # id
        0,  # power
        0,  # toughness
        0,  # temp_buff_power
        0,  # temp_buff_toughness
        empty_food_observation()  # equipped_food
    )


# TODO: add battles after we have action masks
def player_space() -> spaces.Space:
    return spaces.Dict({
        'pets': spaces.Tuple(tuple(pet_space() for _ in range(player.MAX_PETS))),
        'gold': spaces.Discrete(100),
        'lives': spaces.Discrete(100),
        'wins': spaces.Discrete(11),
        'won_last': spaces.Discrete(2),
        'shop_food': spaces.Tuple((food_space(), food_space())),
        'shop_frozen_food': spaces.MultiBinary(shop.MAX_FOOD),
        'shop_pets': spaces.Tuple(tuple(pet_space() for _ in range(shop.MAX_PETS))),
        'shop_frozen_pets': spaces.MultiBinary(shop.MAX_PETS),
        'other_team': spaces.Tuple(tuple(pet_space() for _ in range(player.MAX_PETS))),
    })


def player_observation(observed_game: game.Game):
    observed_player = observed_game.player_1
    observed_shop = observed_player.shop
    return {
        'pets': observation_list(observed_player.pets, empty_pet_observation, pet_observation, player.MAX_PETS),
        'gold': observed_player.gold,
        'lives': observed_player.lives,
        'wins': observed_player.wins,
        'won_last': 1 if observed_player.won_last else 0,
        'shop_food': observation_list(observed_shop.food, empty_food_observation,
                                      lambda item: food_observation(item.food), shop.MAX_FOOD),
        'shop_frozen_food': np.array(observation_list(observed_shop.food, lambda: False, lambda item: item.frozen,
                                                      shop.MAX_FOOD)),
        'shop_pets': observation_list(observed_shop.pets, empty_pet_observation, lambda item: pet_observation(item.pet),
                                      shop.MAX_PETS),
        'shop_frozen_pets': np.array(observation_list(observed_shop.pets, lambda: False, lambda item: item.frozen,
                                                      shop.MAX_PETS)),
        'other_team': observation_list(observed_game.player_2.pets, empty_pet_observation, pet_observation,
                                       player.MAX_PETS)
    }


class SapRandomVersusEnv0(gym.Env):
    """Custom environment for having Super Auto Pets run in RL"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(SapRandomVersusEnv0, self).__init__()
        self.action_space_dimension = (
            len(Action),  # action value
            max(shop.MAX_PETS, shop.MAX_FOOD),  # index in shop
            player.MAX_PETS,  # index of pet on my team
        )
        self.action_space = spaces.MultiDiscrete(self.action_space_dimension)

        self.real_observation_space = player_space()
        self.observation_space = spaces.flatten_space(self.real_observation_space)
        self.game: Optional[game.Game] = None
        self.actions_this_turn = 0

    def step(self, action: Tuple[int, int, int]):
        reward = 0

        action_enum: Action = Action.get_action(val=action[0])

        self.actions_this_turn += 1
        p1 = self.game.player_1
        shop_index = action[1]
        pet_index = action[2]
        try:
            if action_enum is Action.END_TURN or self.actions_this_turn > 100:
                p1.end_turn()
                self.game.player_2.perform_buys(self.game.round)
                result = self.game.battle_phase()
                if result is battle.Result.TEAM_1_WINS:
                    # TODO: make this the number of points instead, but this works for now
                    reward += 10 * self.game.player_1.wins
                self.game.start_round()
                reward += player.STARTING_GOLD - self.game.player_1.gold  # reward for gold spent
                p1.start_turn(self.game.round)
                self.actions_this_turn = 0
            elif action_enum is Action.REROLL:
                p1.reroll()
            elif action_enum is Action.BUY_AND_PLACE_PET:
                p1.buy_and_place_pet(shop_index, pet_index)
                reward += 1
            elif action_enum is Action.BUY_AND_COMBINE_PET:
                p1.buy_and_combine_pet(shop_index, pet_index)
                reward += 1
            elif action_enum is Action.BUY_FOOD_FOR_PET:
                p1.buy_and_apply_food(shop_index, pet_index)
                reward += 1
            elif action_enum is Action.TOGGLE_FREEZE_PET:
                p1.shop.toggle_freeze_pet(shop_index)
            elif action_enum is Action.TOGGLE_FREEZE_FOOD:
                p1.shop.toggle_freeze_food(shop_index)
            elif action_enum is Action.SELL_PET:
                p1.sell(pet_index)
            elif action_enum is Action.MOVE_PET:
                p1.move(pet_index, shop_index)
        except (ValueError, IndexError):
            pass  # ignore invalid actions

        done = (not self.game.player_1.has_lives()) or self.game.player_1.wins == 10
        info = player_observation(self.game)
        observation = spaces.flatten(self.real_observation_space, player_observation(self.game))
        return observation, reward, done, info

    def action_masks(self) -> List[bool]:
        return [True for _ in range(sum(self.action_space_dimension))]

    def reset(self):
        self.game = game.Game(
            EnvironmentPlayer(game.create_shop()),
            game.create_random_player()
        )
        self.game.start_round()
        self.game.player_1.start_turn(self.game.round)

        return spaces.flatten(self.real_observation_space, player_observation(self.game))

    def render(self, mode='human'):
        print(self.game.player_1, self.game.player_2)

    def close(self):
        pass


if __name__ == "__main__":
    # TODO add VecEnv
    from stable_baselines3.common.env_checker import check_env
    from sb3_contrib import MaskablePPO
    from sb3_contrib.common.maskable.utils import get_action_masks
    import time

    start = time.time_ns()

    env = SapRandomVersusEnv0()

    check_env(env)

    obs = env.reset()
    model_path = "model_saves/ppo_sap_random_versus.zip"

    if os.path.exists(model_path):
        print("Loading model")
        model = MaskablePPO.load(model_path, env)
    else:
        print("Making new model")
        model = MaskablePPO("MlpPolicy", env, verbose=1)

    seconds_to_train = 60
    timesteps = int(seconds_to_train * 360)  # rough approximation
    print("Training for", timesteps)
    model.learn(total_timesteps=timesteps)
    model.save(model_path)

    bot_wins = 0
    runs = 0
    done = False
    while runs < 100:
        action_masks = get_action_masks(env)
        action, _states = model.predict(obs, action_masks=action_masks)
        obs, rewards, done, info = env.step(action)
        if done:
            if env.game.player_1.wins == 10:
                bot_wins += 1
            obs = env.reset()
            print("Doing run", runs)
            runs += 1

    print("Against a random player, performance", bot_wins, runs)
    print("Time taken", (time.time_ns() - start) * 1e-9)
    print("Time taken per timestep", ((time.time_ns() - start) * 1e-9) / timesteps)
