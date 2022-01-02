import random
from typing import List, Tuple
from sap.pet import Pet, Trigger, TriggerType
from enum import Enum
import logging
from sap.event_queue import EventQueue
from dataclasses import replace


class Result(Enum):
    TEAM_1_WINS = 1
    TEAM_2_WINS = 2
    DRAW = 3
    UNFINISHED = 4


PetTuple = Tuple[Pet, ...]


def copy_team(pets: List[Pet]):
    return [replace(pet) for pet in pets]


class Battle:
    def __init__(self, team_1: List[Pet], team_2: List[Pet]):
        # We want battle buffs to be lost at the end of battle, so copy all pets
        self.team_1 = copy_team(team_1)
        self.team_2 = copy_team(team_2)
        self.event_queue = EventQueue(team_1=self.team_1, team_2=self.team_2)

    def battle(self) -> Result:
        """
        Have the two teams battle, return the result
        """

        logging.info(f"Teams at the start: {self.team_1}, {self.team_2}")

        # First, allow battle starting events to resolve, like e.g. mosquito damage
        self.event_queue.apply_trigger(Trigger(TriggerType.BATTLE_STARTED, None))
        self.event_queue.resolve_events()

        result = self.assess()  # must be after events as battle might be over
        last_teams = ([], [])
        while result == Result.UNFINISHED:
            # We just run rounds until we get a result that isn't unfinished
            self.do_round()
            if (self.team_1, self.team_2) == last_teams:
                pass  # raise ValueError("Game should never loop")
            else:
                last_teams = (copy_team(self.team_1), copy_team(self.team_2))

            logging.info(f"Teams after a round: f{self.team_1}, f{self.team_2}")
            result = self.assess()

        return result

    def do_round(self):
        """
        Run a single round, and return the teams after it
        """
        if not self.team_1 or not self.team_2:
            return

        # Triggers are resolved in power => toughness => random order
        all_pets = self.team_1 + self.team_2
        random.shuffle(all_pets)

        team_1 = self.team_1
        team_2 = self.team_2

        # Resolve things that happen before attacks
        self.event_queue.apply_trigger(Trigger(TriggerType.BEFORE_ATTACK, team_1[0]))
        self.event_queue.apply_trigger(Trigger(TriggerType.BEFORE_ATTACK, team_2[0]))
        self.event_queue.resolve_events()

        # TODO: see if we need a summon phase (https://github.com/manny405/sapai/blob/d388a0873ac9284832a699c5cdf36c9d8b1892f0/sapai/fight.py#L110)
        # TODO: deal with case that before attack kills the front pet, e.g. Rhino

        if team_1 and team_2:
            front_team_1 = team_1[0]
            front_team_2 = team_2[0]
            self.event_queue.append(
                (front_team_2, Trigger(TriggerType.DEAL_DAMAGE, front_team_1, damage=front_team_2.power)))
            self.event_queue.append(
                (front_team_1, Trigger(TriggerType.DEAL_DAMAGE, front_team_2, damage=front_team_1.power)))
            self.event_queue.apply_trigger(Trigger(TriggerType.AFTER_ATTACK, front_team_1))
            self.event_queue.apply_trigger(Trigger(TriggerType.AFTER_ATTACK, front_team_2))
            self.event_queue.resolve_events()

    def assess(self) -> Result:
        """
        Look at the current teams, and see the result of the battle
        """
        if self.team_1 and self.team_2:
            return Result.UNFINISHED
        elif not self.team_1 and not self.team_2:
            return Result.DRAW
        elif self.team_1:
            return Result.TEAM_1_WINS
        elif self.team_2:
            return Result.TEAM_2_WINS
        else:
            raise ValueError("Unexpected team state somehow, failing fast")

    def __repr__(self):
        return f"<Battle team_1={self.team_1}, team_2={self.team_2}, event_queue={self.event_queue}>"


if __name__ == "__main__":
    from pet_impl import *
    from tests.test_helpers import dummy_pet

    b = Battle(
        [dummy_pet("a", 1, 1)],
        [dummy_pet("b", 1, 1)],
    )
    b.battle()
