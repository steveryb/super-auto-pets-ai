import gym
from gym import spaces
from enum import Enum
import sap.player as player
import sap.shop as shop
import sap.pet_impl as pet_impl


class Action(Enum):
    REROLL = 0
    BUY_AND_PLACE_PET = 1
    BUY_AND_COMBINE_PET = 2
    BUY_FOOD_FOR_PET = 3
    END_TURN = 4

    def get_action(self, val: int):
        for action in Action:
            if action.value == val:
                return action
        raise ValueError("Could not find action for value", val)



class SapArenaEnv0(gym.Env):
    """Custom environment for having Super Auto Pets run in RL"""
    metadata = {'render.modes:'['human']}

    def __init__(self):
        super(SapArenaEnv0, self).__init__()
        self.action_space = spaces.MultiDiscrete(len(Action), player.MAX_PLAYER_PETS, max(shop.MAX_PETS, shop.MAX_FOOD))

        # You can see:
        # Your team (up to player.MAX_PETS pets)
        # Shop pets (up to shop.MAX_PETS pets)


        # Food (up to shop.MAX_FOOD food)
        pet_types = len(pet_impl.ID_TO_PET_INFO)
        food_types = len(pet_impl.ID_TO_PET_INFO)
