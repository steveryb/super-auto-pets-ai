import math
from operator import attrgetter
from typing import List, Optional, Type, Tuple, Dict

from sap.pet import Pet, Food, EquipableFood, Trigger, TriggerType, pick_unique_pets, Fly, SingleEatableFood, \
    RandomEatableFood, EatableFood, ZombieFly
from sap.player import Player
from dataclasses import dataclass
from sap.shop import MAX_TIER


class Ant(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=1, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        """Ant adds a buff to a random pet: https://superauto.pet/pet/ant"""
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            for pet in pick_unique_pets(my_team, 1, [self], random_gen=self.random_gen):
                pet.buff(power=self.level * 2, toughness=self.level)

        return []


class Beaver(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đĻĢ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            for pet in pick_unique_pets(trigger.player.pets, 2, exclusion=[self], random_gen=self.random_gen):
                pet.buff(toughness=self.level)

        return []


class Pig(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=1, symbol="đˇ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            trigger.player.gold += self.level

        return []


class Otter(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=1, symbol="đĻĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            for pet in pick_unique_pets(trigger.player.pets, 1, [self], random_gen=self.random_gen):
                pet.buff(power=self.level, toughness=self.level)

        return []


class Duck(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None or trigger.shop is None:
                raise ValueError("Can't resolve sell events with no player or shop")
            for shop_pet in trigger.shop.pets:
                shop_pet.pet.buff(toughness=self.level)

        return []


class Cricket(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.SUMMON_PET, self,
                                    [ZombieCricket.create(power=self.level, toughness=self.level)]))

        return triggers  # no removal, as summoning replaces


class Horse(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=1, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            trigger.pet.temp_buff(power=self.level)
        return []


class Fish(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_LEVELED_UP and trigger.pet == self:
            for pet in my_team:
                if pet != self:
                    pet.buff(power=self.level - 1, toughness=self.level - 1)
        return []


class Mosquito(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.level))

        return triggers


class Crab(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=3, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            max_health = sorted([pet.toughness for pet in my_team if pet != self], reverse=True)
            if max_health:
                self.toughness = max_health[0]

        return []


class Dodo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="đĻ¤")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.BATTLE_STARTED:
            position = my_team.index(self)
            if position > 0:
                my_team[position - 1].buff(math.floor(self.power * 0.5 * self.level))

        return []


class Elephant(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []

        if trigger.type == TriggerType.BEFORE_ATTACK and trigger.pet == self:
            position = my_team.index(self)
            for pet in my_team[position + 1: position + self.level + 1]:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=1))

        return triggers


class Flamingo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=1, symbol="đĻŠ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            position = my_team.index(self)
            pets_boosted = 0
            for pet in my_team[position + 1:]:
                # TODO: We keep making the mistake of buffing dead pets, it'd be nice to make this a default
                if pet.toughness > 0:
                    pet.buff(power=self.level, toughness=self.level)
                    pets_boosted += 1
                if pets_boosted == 2:
                    break

        return []


class Hedgehog(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=2, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []

        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.DEAL_DAMAGE_TO_ALL, self, damage=2 * self.level))

        return triggers


class Peacock(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=5, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            self.buff(power=self.level * 2)

        return []


class Rat(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=5, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(
                Trigger(TriggerType.SUMMON_PET_OTHER_TEAM, None, summoned_pets=[DirtyRat.create(self.experience)]))

        return triggers


class Shrimp(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:

        if trigger.type == TriggerType.PET_SOLD:
            for pet in pick_unique_pets(my_team, 1, [self], random_gen=self.random_gen):
                pet.buff(toughness=self.level)

        return []


class Spider(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đˇī¸")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            summoned_pet = self.random_gen.choice(PET_TIERS[2]).spawn()
            summoned_pet.toughness = 2
            summoned_pet.power = 2
            summoned_pet.experience = self.experience
            triggers.append(Trigger(TriggerType.SUMMON_PET, self, [summoned_pet]))

        return triggers  # no removal, as summoning replaces


class Swan(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=3, symbol="đĻĸ")

    def start_turn(self, player: "Player"):
        super().start_turn(player)
        player.gold += self.level


class Dog(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            if self.random_gen.choice([True, False]):
                self.buff(power=self.level)
            else:
                self.buff(toughness=self.level)
        return []


class Badger(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=4, symbol="đĻĄ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            my_position = my_team.index(self)
            if my_position == 0:  # front, should attack other pet
                for pet in other_team:
                    if pet.toughness <= 0:
                        continue
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.power))
                    break
            else:  # not front, all within my team
                for pet in my_team[my_position - 1::-1]:
                    if pet.toughness > 0:
                        triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.power))
                        break

            # behind me
            for pet in my_team[my_position + 1:]:
                if pet.toughness > 0:
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.power))
                    break

        return triggers


class Blowfish(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="đĄ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.level * 2))

        return triggers


class Camel(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=5, symbol="đĒ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            my_position = my_team.index(self)
            for pet in my_team[my_position + 1:]:
                if pet.toughness > 0:
                    pet.buff(power=self.level, toughness=2 * self.level)
                    break

        return []


class Giraffe(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:

        if trigger.type == TriggerType.TURN_ENDED:
            my_position = my_team.index(self)
            pets_buffed = 0
            i = my_position - 1
            while i > 0 and pets_buffed < self.level:
                pet = my_team[i]
                if pet.toughness > 0:
                    pet.buff(power=1, toughness=1)
                    pets_buffed += 1
                i -= 1

        return []


class Kangaroo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                self.buff(power=self.level * 2, toughness=self.level * 2)

        return []


class Ox(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=4, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet in my_team and self in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                self.buff(power=2 * self.level)
                self.equipped_food = Melon.spawn()

        return triggers


class Rabbit(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=2, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_EATEN_SHOP_FOOD and trigger.pet in my_team:
            trigger.pet.buff(toughness=self.level)

        return triggers


class Sheep(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.SUMMON_PET, self,
                                    [Ram.create(power=2 * self.level, toughness=2 * self.level),
                                     Ram.create(power=2 * self.level, toughness=2 * self.level)]))

        return triggers  # no removal, as summoning replaces


class Snail(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            if trigger.player.won_last is False:  # can be None
                for pet in my_team:
                    if pet == self:
                        continue
                    pet.buff(power=2 * self.level, toughness=self.level)

        return []


class Turtle(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đĸ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            my_position = my_team.index(self)
            if my_position != len(my_team) - 1:
                my_team[my_position + 1].equipped_food = Melon.spawn()

        return []


class Whale(Pet):
    swallowed_pet: Optional[Pet] = None

    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=6, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            my_position = my_team.index(self)
            for pet in my_team[my_position - 1::-1]:
                if pet.toughness > 0:
                    self.swallowed_pet = pet
                    triggers.append(Trigger(TriggerType.FAINT_PET, pet))
                    break
        elif trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            pets_to_summon = []
            if self.swallowed_pet:
                pet_to_summon = self.swallowed_pet.__class__.spawn()
                # Give it the appropriate level
                pet_to_summon.experience = self.experience
                buff = 0
                if self.level == 2:
                    buff = 2
                if self.level == 3:
                    buff = 5
                pet_to_summon.buff(power=buff, toughness=buff)
                pets_to_summon.append(pet_to_summon)

            triggers.append(Trigger(TriggerType.SUMMON_PET, self, summoned_pets=pets_to_summon))

        return triggers  # we have a summon on faint


class Bison(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=6, symbol="đĻŦ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:

        if trigger.type == TriggerType.TURN_ENDED:
            level_three_in_team = any(pet for pet in my_team if pet != self and pet.level == 3)
            if level_three_in_team:
                self.buff(power=self.level * 2, toughness=self.level * 2)

        return []


class Deer(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=1, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.SUMMON_PET, self,
                                    [Bus.create(power=5 * self.level, toughness=5 * self.level)]))

        return triggers  # no removal, as summoning replaces


class Squirrel(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đŋī¸")

    def start_turn(self, player: "Player"):
        for shop_food in player.shop.food:
            shop_food.food.cost = max(0, shop_food.food.cost - self.level)


class Worm(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="đĒą")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_EATEN_SHOP_FOOD and trigger.pet == self:
            self.buff(power=self.level, toughness=self.level)

        return []


class Dolphin(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=6, symbol="đŦ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            lowest_health_opponents = sorted([pet for pet in other_team if pet.toughness > 0],
                                             key=attrgetter("toughness"))
            if lowest_health_opponents:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, lowest_health_opponents[0], damage=5 * self.level))

        return triggers


class Hippo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=4, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_KNOCKED_OUT_BY and trigger.pet == self:
            self.buff(power=self.level * 2, toughness=self.level * 2)

        return []


class Penguin(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đ§")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            for pet in my_team:
                if pet != self and pet.level >= 2:
                    pet.buff(power=self.level, toughness=self.level)

        return []


class Rooster(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=3, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            summoned_pets = []
            for _ in range(self.level):
                summoned_pets.append(Chick.create(power=self.power // 2))
            triggers.append(Trigger(TriggerType.SUMMON_PET, self, summoned_pets=summoned_pets))

        return triggers  # no removal, as summoning replaces


class Skunk(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=6, symbol="đĻ¨")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            highest_health_opponents = sorted([pet for pet in other_team if pet.toughness > 0],
                                              key=attrgetter("toughness"), reverse=True)
            if highest_health_opponents:
                health_ratio = 0.33
                if self.level == 2:
                    health_ratio = 0.66
                elif self.level == 3:
                    health_ratio = 1
                triggers.append(
                    Trigger(TriggerType.REDUCE_HEALTH, highest_health_opponents[0], health_ratio=health_ratio))

        return triggers


class Monkey(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            my_team[0].buff(power=3 * self.level, toughness=3 * self.level)

        return []


class Cow(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=6, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            trigger.player.shop.replace_shop([
                Milk.create(power=self.level, toughness=2 * self.level),
                Milk.create(power=self.level, toughness=2 * self.level)
            ])
        return []


class Crocodile(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=8, toughness=4, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in other_team[::-1]:
                if pet.toughness > 0:
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=8 * self.level))
                    break

        return triggers


class Rhino(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=8, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_KNOCKED_OUT_BY and trigger.pet == self and self.toughness > 0:
            for pet in other_team:
                if pet.toughness > 0:
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE_TO_FRONT, None, damage=self.level * 4, index=0))
                    break

        return triggers


class Scorpion(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=1, symbol="đĻ", equipped_food=Peanut.create())


class Seal(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=8, symbol="đĻ­")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_EATEN_SHOP_FOOD and trigger.pet == self:
            for pet in pick_unique_pets(my_team, 2, [self]):
                pet.buff(power=self.level, toughness=self.level)

        return []


class Shark(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=4, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet in my_team and self.toughness > 0:
            self.buff(power=self.level * 2, toughness=self.level)
        return []


class Turkey(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=4, symbol="đĻ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            trigger.pet.buff(power=self.level * 3, toughness=self.level * 3)
        return []


class Boar(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=8, toughness=6, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.BEFORE_ATTACK and trigger.pet == self:
            self.buff(power=2 * self.level, toughness=2 * self.level)

        return []


class Cat(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=5, symbol="đą")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_EATEN_SHOP_FOOD and trigger.pet in my_team:
            if isinstance(trigger.food, EatableFood):
                trigger.pet.buff(power=trigger.food.power * self.level, toughness=trigger.food.toughness * self.level)

        return triggers


class Dragon(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=8, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and type(trigger.pet) in PET_TIERS[0]:
            for pet in my_team:
                pet.buff(power=self.level, toughness=self.level)

        return []


class Gorilla(Pet):
    num_triggers: int = 1

    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=9, symbol="đĻ")

    def start_turn(self, player: "Player"):
        super().start_turn(player)
        self.num_triggers = 1

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            self.num_triggers = 1
        elif trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self and self.num_triggers:
            self.num_triggers = 0
            self.equipped_food = Coconut.create()

        return []


class Leopard(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=10, toughness=4, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in pick_unique_pets(other_team, self.level, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=math.floor(0.5 * self.power)))

        return triggers


class Mammoth(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=10, symbol="đĻŖ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            for pet in my_team:
                if pet.toughness > 0 and pet != self:
                    pet.buff(power=self.level * 2, toughness=self.level * 2)

        return []


class Snake(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=6, symbol="đ")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=5 * self.level))

        return triggers


class Tiger(Pet):
    in_battle: bool = False

    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=3, symbol="đ")

    def start_turn(self, player: "Player"):
        self.in_battle = False

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            self.in_battle = True

        triggers = []
        my_position = my_team.index(self)
        if my_position > 0:
            in_front_pet = my_team[my_position - 1]
            if in_front_pet.toughness > 0:
                triggers.extend(in_front_pet.apply_trigger(Trigger(
                    TriggerType.FORWARD_TRIGGER, None, forwarded_trigger=trigger, trigger_experience=self.experience),
                    my_team, other_team))

        return triggers


# ---------------------------------------------------------------------------------------------------------------------
# Summoned pets
# ---------------------------------------------------------------------------------------------------------------------

class ZombieCricket(Pet):
    @classmethod
    def spawn(cls):
        return cls.create(power=1, toughness=1)

    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="đ§đĻ")


class DirtyRat(Pet):
    @classmethod
    def spawn(cls):
        return cls.create(experience=0)

    @classmethod
    def create(cls, experience: int):
        return cls(power=1, toughness=1, symbol="đĻšđ", experience=experience)

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, trigger.pet, damage=self.level))

        return triggers


class Ram(Pet):
    @classmethod
    def spawn(cls):
        return cls.create(power=2, toughness=2)

    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="đ")


class Chick(Pet):
    @classmethod
    def spawn(cls):
        return cls.create(power=1)

    @classmethod
    def create(cls, power: int):
        return cls(power=power, toughness=1, symbol="đ¤")


class Bee(Pet):
    @classmethod
    def spawn(cls):
        return cls.create()

    @classmethod
    def create(cls):
        return cls(power=1, toughness=1, symbol="đ")


class Bus(Pet):
    @classmethod
    def spawn(cls):
        return cls.create(power=5, toughness=5)

    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="đ", equipped_food=Chili.spawn())


# Food
class Apple(SingleEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3, power=1, toughness=1)


class Cupcake(SingleEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ§", cost=3, power=3, toughness=3)

    def feed(self, pet: "Pet"):
        pet.temp_buff(power=3, toughness=3)


class Honey(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ¯", cost=3)

    def summoned_pets(self, pet: "Pet") -> List["Pet"]:
        return [Bee.create()]


class MeatBone(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3)

    def enhance_attack(self, pet: "Pet", other_team: List["Pet"], damage_trigger: Trigger) -> List[Trigger]:
        damage_trigger.damage += 5
        return [damage_trigger]


class SleepingPill(Food):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=1)

    def apply(self, player: "Player", pet: Optional["Pet"] = None) -> List[Pet]:
        player.take_action(pet, Trigger(TriggerType.FAINT_PET, pet))
        return [pet]


class Garlic(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ§", cost=3)

    def reduce_damage(self, pet: Optional["Pet"], damage: int) -> int:
        return max(1, damage - 2)  # always take at least one damage, sadly


class SaladBowl(RandomEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đĨ", cost=3, power=1, toughness=1, targets=2)


class Pear(SingleEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3, power=2, toughness=2)


class CannedFood(Food):
    @classmethod
    def spawn(cls):
        return cls(symbol="đĨĢ", cost=3)

    def apply(self, player: "Player", pet: Optional["Pet"] = None):
        player.shop.buff(power=2, toughness=1)
        return []


class Chili(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đļī¸", cost=3)

    def enhance_attack(self, pet: "Pet", other_team: List["Pet"], damage_trigger: Trigger) -> List[Trigger]:
        if len(other_team) > 1:
            return [damage_trigger, Trigger(TriggerType.DEAL_DAMAGE, other_team[1], damage=5)]
        return [damage_trigger]


class Chocolate(Food):
    @classmethod
    def spawn(cls):
        return cls(symbol="đĢ", cost=3)

    def apply(self, player: "Player", pet: Optional["Pet"] = None) -> List[Pet]:
        player.add_experience(pet, 1)
        return [pet]


class Sushi(RandomEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đŖ", cost=3, power=1, toughness=1, targets=3)


class Melon(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3)

    def reduce_damage(self, pet: Optional["Pet"], damage: int) -> int:
        pet.equipped_food = None
        return max(0, damage - 20)


class Pizza(RandomEatableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3, targets=2, power=2, toughness=2)


class Steak(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đĨŠ", cost=3)

    def enhance_attack(self, pet: "Pet", other_team: List["Pet"], damage_trigger: Trigger) -> List[Trigger]:
        damage_trigger.damage += 20
        pet.equipped_food = None
        return [damage_trigger]


class Mushroom(EquipableFood):
    @classmethod
    def spawn(cls):
        return cls(symbol="đ", cost=3)

    def summoned_pets(self, pet: Pet) -> List["Pet"]:
        new_pet = pet.__class__.spawn()
        new_pet.power = 1
        new_pet.toughness = 1
        new_pet.experience = pet.experience
        return [new_pet]


class Milk(SingleEatableFood):
    @classmethod
    def spawn(cls):
        raise NotImplementedError("Cannot spawn milk without specifying how powerful it is")

    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(symbol="đĨ", cost=0, power=power, toughness=toughness)


class Peanut(EquipableFood):
    @classmethod
    def spawn(cls):
        raise NotImplementedError("Cannot spawn milk without specifying how powerful it is")

    @classmethod
    def create(cls):
        return cls(symbol="đĨ", cost=0)

    def enhance_attack(self, pet: "Pet", other_team: List["Pet"], damage_trigger: Trigger) -> List[Trigger]:
        return [
            Trigger(TriggerType.DEAL_POISON_DAMAGE, damage_trigger.pet, damage=damage_trigger.damage)
        ]


class Coconut(EquipableFood):
    @classmethod
    def spawn(cls):
        raise NotImplementedError("Cannot spawn milk without specifying how powerful it is")

    @classmethod
    def create(cls):
        return cls(symbol="đĨĨ", cost=0)

    def reduce_damage(self, pet: Optional["Pet"], damage: int) -> int:
        pet.equipped_food = None
        return 0


@dataclass
class FoodInfo:
    food_type: Type[Food]
    tier: int


ID_TO_FOOD_INFO: Dict[int, FoodInfo] = {
    0: FoodInfo(None, -1),
    1: FoodInfo(Honey, 0),
    2: FoodInfo(Cupcake, 1),
    3: FoodInfo(MeatBone, 1),
    4: FoodInfo(SleepingPill, 1),
    5: FoodInfo(Garlic, 2),
    6: FoodInfo(SaladBowl, 2),
    7: FoodInfo(CannedFood, 3),
    8: FoodInfo(Pear, 3),
    9: FoodInfo(Chili, 4),
    10: FoodInfo(Chocolate, 4),
    11: FoodInfo(Sushi, 4),
    12: FoodInfo(Melon, 5),
    13: FoodInfo(Pizza, 5),
    14: FoodInfo(Steak, 5),
    15: FoodInfo(Mushroom, 5),
    16: FoodInfo(Coconut, -1),
    17: FoodInfo(Peanut, -1),
    18: FoodInfo(Milk, -1),
    19: FoodInfo(Apple, 0),
}

FOOD_TYPE_TO_ID = {info.food_type: key for key, info in ID_TO_FOOD_INFO.items()}

FOOD_TIERS: List[List[Type[Food]]] = [
    [info.food_type for info in ID_TO_FOOD_INFO.values() if info.tier == tier]
    for tier in range(0, MAX_TIER)
]


@dataclass
class PetInfo:
    pet_type: Type[Pet]
    tier: int


ID_TO_PET_INFO: Dict[int, PetInfo] = {
    0: PetInfo(None, -1),
    1: PetInfo(Beaver, 0),
    2: PetInfo(Cricket, 0),
    3: PetInfo(Duck, 0),
    4: PetInfo(Fish, 0),
    5: PetInfo(Horse, 0),
    6: PetInfo(Mosquito, 0),
    7: PetInfo(Otter, 0),
    8: PetInfo(Crab, 1),
    9: PetInfo(Dodo, 1),
    10: PetInfo(Elephant, 1),
    11: PetInfo(Flamingo, 1),
    12: PetInfo(Hedgehog, 1),
    13: PetInfo(Peacock, 1),
    14: PetInfo(Rat, 1),
    15: PetInfo(Shrimp, 1),
    16: PetInfo(Spider, 1),
    17: PetInfo(Swan, 1),
    18: PetInfo(Dog, 2),
    19: PetInfo(Badger, 2),
    20: PetInfo(Blowfish, 2),
    21: PetInfo(Camel, 2),
    22: PetInfo(Giraffe, 2),
    23: PetInfo(Kangaroo, 2),
    24: PetInfo(Ox, 2),
    25: PetInfo(Rabbit, 2),
    26: PetInfo(Sheep, 2),
    27: PetInfo(Whale, 3),
    28: PetInfo(Bison, 3),
    29: PetInfo(Deer, 3),
    30: PetInfo(Dolphin, 3),
    31: PetInfo(Hippo, 3),
    32: PetInfo(Penguin, 3),
    33: PetInfo(Rooster, 3),
    34: PetInfo(Skunk, 3),
    35: PetInfo(Squirrel, 3),
    36: PetInfo(Worm, 3),
    37: PetInfo(Monkey, 4),
    38: PetInfo(Cow, 4),
    39: PetInfo(Crocodile, 4),
    40: PetInfo(Rhino, 4),
    41: PetInfo(Scorpion, 4),
    42: PetInfo(Seal, 4),
    43: PetInfo(Shark, 4),
    44: PetInfo(Turkey, 4),
    45: PetInfo(Boar, 5),
    46: PetInfo(Cat, 5),
    47: PetInfo(Dragon, 5),
    48: PetInfo(Gorilla, 5),
    49: PetInfo(Fly, 5),
    50: PetInfo(Leopard, 5),
    51: PetInfo(Mammoth, 5),
    52: PetInfo(Snake, 5),
    53: PetInfo(ZombieCricket, -1),
    54: PetInfo(DirtyRat, -1),
    55: PetInfo(Ram, -1),
    56: PetInfo(Chick, -1),
    57: PetInfo(ZombieFly, -1),
    58: PetInfo(Bee, -1),
    59: PetInfo(Bus, -1),
    60: PetInfo(Ant, 0),
}

PET_TYPE_TO_ID = {info.pet_type: key for key, info in ID_TO_PET_INFO.items()}

PET_TIERS: List[List[Type[Pet]]] = [
    [info.pet_type for info in ID_TO_PET_INFO.values() if info.tier == tier]
    for tier in range(0, MAX_TIER)
]
