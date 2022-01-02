from sap.pet import Pet, Trigger, TriggerType, Fly, pick_unique_pets
from dataclasses import replace
from sap.player import Player
from sap.shop import Shop
from abc import ABC, abstractmethod
import math
from operator import attrgetter

from typing import List, Optional, Type, Tuple
import logging


class Ant(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=1, symbol="🐜")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        """Ant adds a buff to a random pet: https://superauto.pet/pet/ant"""
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            for pet in pick_unique_pets(my_team, 1, [self], random_gen=self.random_gen):
                pet.buff(power=self.level * 2, toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Beaver(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="🦫")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            for pet in pick_unique_pets(trigger.player.pets, 2, exclusion=[self], random_gen=self.random_gen):
                pet.buff(toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Pig(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=1, symbol="🐷")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            trigger.player.gold += self.level

        return super()._resolve_trigger(trigger, my_team, other_team)


class Otter(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=1, symbol="🦦")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            if trigger.player is None:
                raise ValueError("Can't resolve sell events with no player")
            for pet in pick_unique_pets(trigger.player.pets, 1, [self], random_gen=self.random_gen):
                pet.buff(power=self.level, toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Duck(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="🦆")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_SOLD and trigger.pet == self:
            if trigger.player is None or trigger.shop is None:
                raise ValueError("Can't resolve sell events with no player or shop")
            for shop_pet in trigger.shop.pets:
                shop_pet.pet.buff(toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Cricket(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="🦗")

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
        return cls(power=2, toughness=1, symbol="🐎")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            trigger.pet.temp_buff(power=self.level)
        return super()._resolve_trigger(trigger, my_team, other_team)


class Fish(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="🐟")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_LEVELED_UP and trigger.pet == self:
            for pet in my_team:
                if pet != self:
                    pet.buff(power=self.level, toughness=self.level)
        return super()._resolve_trigger(trigger, my_team, other_team)


class Mosquito(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="🦟")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.level))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Crab(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=3, symbol="🦀")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_BOUGHT and trigger.pet == self:
            max_health = sorted([pet.toughness for pet in my_team if pet != self], reverse=True)
            if max_health:
                self.toughness = max_health[0]

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Dodo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="🦤")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            position = my_team.index(self)
            if position > 0:
                my_team[position - 1].buff(math.floor(self.power * 0.5 * self.level))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Elephant(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="🐘")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []

        if trigger.type == TriggerType.BEFORE_ATTACK and trigger.pet == self:
            position = my_team.index(self)
            for pet in my_team[position + 1: position + self.level + 1]:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=1))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Flamingo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=1, symbol="🦩")

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

        return super()._resolve_trigger(trigger, my_team, other_team)


class Hedgehog(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=2, symbol="🦔")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []

        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(Trigger(TriggerType.DEAL_DAMAGE_TO_ALL, self, damage=2 * self.level))

        return super()._resolve_trigger(trigger, my_team, other_team) + triggers


class Peacock(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=5, symbol="🦚")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            self.buff(power=self.level * 2)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Rat(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=5, symbol="🐀")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            triggers.append(
                Trigger(TriggerType.SUMMON_PET_OTHER_TEAM, None, summoned_pets=[DirtyRat.create(self.experience)]))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Shrimp(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=3, symbol="🦐")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:

        if trigger.type == TriggerType.PET_SOLD:
            for pet in pick_unique_pets(my_team, 1, [self], random_gen=self.random_gen):
                pet.buff(toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Spider(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="🕷️")

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
        return cls(power=3, toughness=3, symbol="🦢")

    def start_turn(self, player: "Player"):
        super().start_turn(player)
        player.gold += self.level


class Dog(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="🐕")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            if self.random_gen.choice([True, False]):
                self.buff(power=self.level)
            else:
                self.buff(toughness=self.level)
        return super()._resolve_trigger(trigger, my_team, other_team)


class Badger(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=4, symbol="🦡")

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

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Blowfish(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="🐡")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=self.level * 2))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Camel(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=5, symbol="🐪")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_DAMAGED and trigger.pet == self:
            my_position = my_team.index(self)
            for pet in my_team[my_position + 1:]:
                if pet.toughness > 0:
                    pet.buff(power=self.level, toughness=2 * self.level)
                    break

        return super()._resolve_trigger(trigger, my_team, other_team)


class Giraffe(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=5, symbol="🦒")

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

        return super()._resolve_trigger(trigger, my_team, other_team)


class Kangaroo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="🦘")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                self.buff(power=self.level * 2, toughness=self.level * 2)

        return super()._resolve_trigger(trigger, my_team, other_team) + triggers


class Sheep(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=2, symbol="🐑")

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
        return cls(power=2, toughness=2, symbol="🐌")

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

        return super()._resolve_trigger(trigger, my_team, other_team)


class Whale(Pet):
    swallowed_pet: Optional[Pet] = None

    @classmethod
    def spawn(cls):
        return cls(power=2, toughness=6, symbol="🐋")

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
        return cls(power=6, toughness=6, symbol="🦬")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:

        if trigger.type == TriggerType.TURN_ENDED:
            level_three_in_team = any(pet for pet in my_team if pet != self and pet.level == 3)
            if level_three_in_team:
                self.buff(power=self.level * 2, toughness=self.level * 2)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Dolphin(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=6, symbol="🐬")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            lowest_health_opponents = sorted([pet for pet in other_team if pet.toughness > 0],
                                             key=attrgetter("toughness"))
            if lowest_health_opponents:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, lowest_health_opponents[0], damage=5 * self.level))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Hippo(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=4, symbol="🦛")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_KNOCKED_OUT_BY and trigger.pet == self:
            self.buff(power=self.level * 2, toughness=self.level * 2)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Penguin(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="🐧")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.TURN_ENDED:
            for pet in my_team:
                if pet != self and pet.level >= 2:
                    pet.buff(power=self.level, toughness=self.level)

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Rooster(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=3, symbol="🐓")

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
        return cls(power=4, toughness=6, symbol="🦨")

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

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Monkey(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=1, toughness=2, symbol="🐒")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.TURN_ENDED:
            my_team[0].buff(power=3 * self.level, toughness=3 * self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Crocodile(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=8, toughness=4, symbol="🐊")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in other_team[::-1]:
                if pet.toughness > 0:
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=8 * self.level))
                    break

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Rhino(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=5, toughness=8, symbol="🦏")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.PET_KNOCKED_OUT_BY and trigger.pet == self and self.toughness > 0:
            for pet in other_team:
                if pet.toughness > 0:
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE_TO_FRONT, None, damage=self.level * 4, index=0))
                    break

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Shark(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=4, symbol="🦈")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet in my_team and self.toughness > 0:
            self.buff(power=self.level * 2, toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Turkey(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=4, symbol="🦃")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.PET_SUMMONED and trigger.pet in my_team and trigger.pet != self:
            trigger.pet.buff(power=self.level * 3, toughness=self.level * 3)
        return super()._resolve_trigger(trigger, my_team, other_team)


class Boar(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=8, toughness=6, symbol="🐗")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        if trigger.type == TriggerType.BEFORE_ATTACK and trigger.pet == self:
            self.buff(power=2 * self.level, toughness=2 * self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Dragon(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=8, symbol="🐉")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_BOUGHT and type(trigger.pet) in PET_TIERS[0]:
            for pet in my_team:
                pet.buff(power=self.level, toughness=self.level)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Leopard(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=10, toughness=4, symbol="🐆")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> \
            List[Trigger]:
        triggers = []
        if trigger.type == TriggerType.BATTLE_STARTED:
            for pet in pick_unique_pets(other_team, self.level, [], random_gen=self.random_gen):
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=math.floor(0.5 * self.power)))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Mammoth(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=3, toughness=10, symbol="🦣")

    def _resolve_trigger(self, trigger: Trigger, my_team: List[Pet], other_team: List[Pet]) -> List[
        Trigger]:
        if trigger.type == TriggerType.PET_FAINTED and trigger.pet == self:
            for pet in my_team:
                if pet.toughness > 0 and pet != self:
                    pet.buff(power=self.level * 2, toughness=self.level * 2)

        return super()._resolve_trigger(trigger, my_team, other_team)


class Snake(Pet):
    @classmethod
    def spawn(cls):
        return cls(power=6, toughness=6, symbol="🐍")

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                for pet in pick_unique_pets(other_team, 1, [], random_gen=self.random_gen):
                    triggers.append(Trigger(TriggerType.DEAL_DAMAGE, pet, damage=5 * self.level))

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class Tiger(Pet):
    in_battle: bool = False

    @classmethod
    def spawn(cls):
        return cls(power=4, toughness=3, symbol="🐅")

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

        return triggers + super()._resolve_trigger(trigger, my_team, other_team)


class SummonedPet(Pet, ABC):
    @classmethod
    def spawn(cls):
        raise NotImplementedError("Should not ever spawn this without creating it manually")


class ZombieCricket(SummonedPet):
    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="🧟🦗")


class DirtyRat(SummonedPet):
    @classmethod
    def create(cls, experience: int):
        return cls(power=1, toughness=1, symbol="🦹🐀", experience=experience)

    def _resolve_trigger(self, trigger: Trigger, my_team: List["Pet"], other_team: Optional[List["Pet"]]) -> List[
        Trigger]:
        triggers = []
        if trigger.type == TriggerType.AFTER_ATTACK and trigger.pet in my_team:
            if my_team.index(trigger.pet) == my_team.index(self) - 1:
                triggers.append(Trigger(TriggerType.DEAL_DAMAGE, trigger.pet, damage=self.level))

        return super()._resolve_trigger(trigger, my_team, other_team) + triggers


class Ram(SummonedPet):
    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="🐏")


class Chick(SummonedPet):
    @classmethod
    def create(cls, power: int):
        return cls(power=power, toughness=1, symbol="🐤")


class ZombieFly(SummonedPet):
    @classmethod
    def create(cls, power: int, toughness: int):
        return cls(power=power, toughness=toughness, symbol="🧟🪰")

class Bee(SummonedPet):
    @classmethod
    def create(cls):
        return cls(power=1, toughness=1, symbol="🐝")


PET_TIERS: Tuple[Tuple[Type[Pet], ...], ...] = (
    (Ant, Beaver, Cricket, Duck, Fish, Horse, Mosquito, Otter, Pig),
    (Crab, Dodo, Elephant, Flamingo, Hedgehog, Peacock, Rat, Shrimp, Spider, Swan),
    (Dog, Badger, Blowfish, Camel, Giraffe, Kangaroo, Sheep),  # TODO: ox, rabbit, turtle (food)
    (Whale, Bison, Dolphin, Hippo, Penguin, Rooster, Skunk),  # TODO: deer, squirrel, worm (food)
    (Monkey, Crocodile, Rhino, Shark, Turkey),  # TODO: cow, scorpion, seal (food)
    (Boar, Dragon, Fly, Leopard, Mammoth, Snake, Tiger)  # TODO: cat, gorilla, (food)
)
