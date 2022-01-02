from abc import ABC, abstractmethod
from enum import Enum
from random import Random
from typing import List, Optional, Tuple
from sap.event_queue import EventQueue

from sap.pet import Pet, Trigger, TriggerType
from sap.shop import Shop

import logging

PET_COST = 3
REROLL_COST = 1


class Player(ABC):
    def __init__(self, name: str, pets: List[Optional[Pet]] = None):
        self.name = name

        if pets is None:
            pets = []

        self.pets: List[Optional[Pet]] = pets
        self.gold = 0
        self.lives = 10
        self.wins = 0
        self.won_last: Optional[bool] = None

    def start_turn(self, round: int):
        self.gold = 10
        round += 1
        for pet in self.pets:
            pet.start_turn(self)

    def num_pets(self) -> int:
        """
        Number of non-null pets
        """
        return len([pet for pet in self.pets if pet is not None])

    def can_buy(self):
        """
        Whether this player can buy or not
        """
        return self.gold >= PET_COST

    def _buy(self, shop: Shop, shop_position: int) -> Pet:
        """
        Buy a given pet, and place it at the given position
        """
        if not self.can_buy():
            raise ValueError("Cannot buy when we don't have enough gold")
        pet = shop.buy(shop_position)
        self.gold -= PET_COST
        return pet

    def buy_and_place(self, shop: Shop, shop_position: int, target_position: int) -> Pet:
        """Buy pet and place it down"""
        pet = self._buy(shop, shop_position)
        self.place_pet(pet, target_position)
        self.apply_trigger(Trigger(TriggerType.PET_BOUGHT, pet, player=self, shop=shop))
        self.apply_trigger(Trigger(TriggerType.PET_SUMMONED, pet, player=self, shop=shop))
        return pet

    def combine(self, pet: Pet, target_position: int):
        """Combine a pet with another"""
        target_pet = self.pets.pop(target_position)
        if target_pet is None:
            raise ValueError("Can't combine a pet if it's None")
        lower_level_pet, higher_level_pet = sorted([target_pet, pet], key=lambda p: p.experience)
        old_level = higher_level_pet.level
        higher_level_pet.combine(lower_level_pet)
        self.place_pet(higher_level_pet, target_position)

        if old_level != higher_level_pet.level:
            self.apply_trigger(Trigger(TriggerType.PET_LEVELED_UP, higher_level_pet, player=self))


    def buy_and_combine(self, shop: Shop, shop_position: int, target_position: int) -> Pet:
        """Buy a pet and combine it with another"""
        pet = self._buy(shop, shop_position)
        new_pet = self.pets[target_position]
        new_pet.combine(pet)
        self.apply_trigger(Trigger(TriggerType.PET_BOUGHT, new_pet, player=self, shop=shop))
        return new_pet

    def place_pet(self, pet: Pet, target: int) -> List[Pet]:
        """
        Take the given pet, and move it to the given index
        """
        # Note, this isn't summoning a pet, as we use this in the internals when we're not necessarily summoning
        if self.num_pets() >= 5:
            raise ValueError("Already full up on pets")
        elif target < 0 or target >= 5:
            raise IndexError("Invalid position for a pet")
        else:
            self.pets.insert(target, pet)
        return self.pets

    def condense(self) -> List[Pet]:
        """
        Remove all null pets
        """
        for i in [i for i in range(len(self.pets)) if self.pets[i] is None][::-1]:
            self.pets.pop(i)

        return self.pets

    def trigger_win(self):
        self.wins += 1
        self.won_last = True

    def trigger_loss(self, round: int):
        if round <= 2:
            self.lives -= 1
        elif 2 < round <= 4:
            self.lives -= 2
        else:
            self.lives -= 3
        self.won_last = False

    def trigger_draw(self):
        self.won_last = None

    def has_lives(self):
        """
        :return: whether the player has any lives left or not
        """
        return self.lives > 0

    def perform_buys(self, shop: Shop, round: int):
        """
        Wrapper around buy_phase, to set up the phase
        """
        self.start_turn(round)
        shop.setup_for_round(round)
        self.buy_phase(shop)
        self.condense() # make sure there's no gaps
        self.apply_trigger(Trigger(TriggerType.TURN_ENDED, None))

    def reroll(self, shop: Shop):
        """
        Reroll the shop, taking the gold required
        """
        if self.can_reroll():
            shop.reroll()
            self.gold -= REROLL_COST
        else:
            raise ValueError("Do not have enough gold to reroll", self.gold)

    def can_reroll(self):
        return self.gold >= REROLL_COST

    def remove_pet(self, position: int) -> Pet:
        """Remove pet form listing"""
        if self.pets[position] is None:
            raise IndexError("Position does not contain a pet", position)
        return self.pets.pop(position)

    def sell(self, position: int, shop: Shop) -> Pet:
        """
        Sell the given pet
        """
        sold_pet = self.pets[position]
        self.apply_trigger(Trigger(TriggerType.PET_SOLD, sold_pet, player=self, shop=shop))
        self.remove_pet(position)
        self.gold += 1
        return sold_pet

    def apply_trigger(self, trigger: Trigger):
        """Apply a trigger to all pets, and resolve the action queue"""
        event_queue = EventQueue(team_1=self.pets, team_2=[])
        event_queue.apply_trigger(trigger)
        event_queue.resolve_events()

    @abstractmethod
    def buy_phase(self, shop: Shop):
        raise NotImplementedError()

    def __repr__(self):
        return f"<Player name={self.name}, wins={self.wins}, lives={self.lives} pets={self.pets}>"


class RandomPlayer(Player):
    def __init__(self, random_gen: Random):
        super().__init__("Random Player")
        self.random = random_gen

    def buy_phase(self, shop: Shop):
        self.condense()
        if self.num_pets():
            sell_position = self.random.randint(0, self.num_pets() - 1)
            self.sell(sell_position, shop)
        while self.can_buy() and self.num_pets() < 5 and shop.num_pets():
            shop_position = self.random.randint(0, len(shop.pets) - 1)
            while shop.pets[shop_position] is None:
                shop_position = self.random.randint(0, len(shop.pets) - 1)
            self.buy_and_place(shop, shop_position, self.random.randint(0, 4))


class Action(Enum):
    BUY_AND_PLACE = "BP"
    BUY_AND_COMBINE = "BC"
    REROLL = "R"
    FREEZE = "F"
    SELL = "S"
    COMBINE = "C"

    @staticmethod
    def get(value: str) -> Optional["Action"]:
        for action in Action:
            if action.value == value:
                return action

        return None


class RealPlayer(Player):
    def __init__(self):
        super().__init__("Real Player")

    def buy_phase(self, shop: Shop):
        while self.gold >= PET_COST:
            print("Shop", shop)
            print("Current team", self)
            action = Action.get(input("Action? Available:" + ", ".join(f"{action.name} ({action.value})" for action in Action) + " "))

            if action is Action.REROLL:
                if self.can_reroll():
                    self.reroll(shop)
                else:
                    print("Not enough to reroll, repeating")
            elif action is Action.BUY_AND_PLACE or action is Action.BUY_AND_COMBINE:
                shop_index = int(input("Which to buy? "))
                if shop_index == -1:
                    continue

                if action is Action.BUY_AND_PLACE:
                    target_index = int(input("Where to put it? "))
                    self.buy_and_place(shop, shop_index, target_index)
                if action is Action.BUY_AND_COMBINE:
                    target_index = int(input("Which pet to combine with? "))
                    self.buy_and_combine(shop, shop_index, target_index)
            elif action is Action.FREEZE:
                index = int(input("Which to freeze? "))
                shop.toggle_freeze(index)
            elif action is Action.SELL:
                index = int(input("Which to Sell? "))
                self.sell(index, shop)
            elif action is Action.COMBINE:
                source_index = int(input("Where to source from?"))
                pet = self.remove_pet(source_index)
                print("New pets", self.pets)
                target_index = int(input("Where to combine with?"))
                other_pet = self.remove_pet(target_index)
                self.place_pet(pet.combine(other_pet), target_index)
