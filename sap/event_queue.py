import logging
from sap.pet import Trigger, TriggerType, Pet
from typing import Iterable, List
import math
from typing import Tuple, List

Event = Tuple[Pet, Trigger]

class EventQueue:
    def __init__(self, team_1: List[Pet], team_2: List[Pet]):
        self.team_1 = team_1
        self.team_2 = team_2
        self.event_queue: List[Event] = []

    def append(self, event: Event):
        self.event_queue.append(event)

    def extend(self, events: Iterable[Event]):
        self.event_queue.extend(events)

    @property
    def resolve_order(self) -> List[Pet]:
        """
        Events are resolved first by power, then toughness, then random. This is determined at the top of the
        round
        """
        all_pets = self.team_1 + self.team_2
        return sorted(all_pets, key=lambda pet: (pet.power, pet.toughness))

    def apply_trigger(self, trigger: Trigger):
        for pet in self.resolve_order:
            if pet in self.team_1 + self.team_2:
                self.event_queue.append((pet, trigger))

    def deal_damage(self, pet: Pet, damage: int, triggered_pet: Pet):
        logging.debug(f"Dealing damage {pet} {damage}")
        if pet.toughness <= 0:
            logging.debug(f"Skipping damage {pet} {damage} since it's < 0")
            return
        elif damage == 0:
            logging.debug(f"Damage is 0 for {pet}, so skipping")
            return
        else:
            pet.take_damage(damage)

        if pet.toughness <= 0:
            self.apply_trigger(Trigger(TriggerType.PET_FAINTED, pet))
            if triggered_pet.toughness > 0:
                self.apply_trigger(Trigger(TriggerType.PET_KNOCKED_OUT_BY, triggered_pet))
        else:
            self.apply_trigger(Trigger(TriggerType.PET_DAMAGED, pet))

    def resolve_events(self):
        while self.event_queue:
            triggered_pet, trigger = self.event_queue.pop(0)

            my_team = self.team_1 if triggered_pet in self.team_1 else self.team_2
            other_team = self.team_1 if my_team is self.team_2 else self.team_2

            if trigger.type is TriggerType.REMOVE_PET:
                logging.debug(f"Removing pet {trigger.pet}")
                if trigger.pet in my_team:
                    my_team.remove(trigger.pet)
                elif trigger.pet in other_team:
                    other_team.remove(trigger.pet)
            elif trigger.type is TriggerType.SUMMON_PET:
                logging.debug(f"Summoning pet {trigger.pet} {trigger.summoned_pets}")
                index = my_team.index(trigger.pet)
                live_team_members = len([pet for pet in my_team if pet.toughness > 0])
                for summoned_pet in trigger.summoned_pets:
                    if live_team_members <= 4:
                        my_team.insert(index, summoned_pet)
                        self.apply_trigger(Trigger(TriggerType.PET_SUMMONED, summoned_pet))
                        live_team_members += 1
                self.event_queue.append((triggered_pet, Trigger(TriggerType.REMOVE_PET, trigger.pet)))
            elif trigger.type is TriggerType.DEAL_DAMAGE:
                self.deal_damage(trigger.pet, trigger.damage, triggered_pet)
            elif trigger.type is TriggerType.DEAL_DAMAGE_TO_ALL:
                logging.debug(f"Dealing damage to all pets: {trigger.damage}")
                for pet in my_team + other_team:
                    self.deal_damage(pet, trigger.damage, triggered_pet)
            elif trigger.type is TriggerType.DEAL_DAMAGE_TO_FRONT:
                for pet in other_team:
                    if pet.toughness > 0:
                        self.deal_damage(pet, trigger.damage, triggered_pet)
                        break
            elif trigger.type is TriggerType.SUMMON_PET_OTHER_TEAM:
                # mainly for rat, TODO if there's a cleaner way to do this
                logging.debug(f"Summoning on other team {trigger.summoned_pets}")
                for pet in trigger.summoned_pets:
                    if len(other_team) <= 4:
                        other_team.append(pet)

            elif trigger.type is TriggerType.FAINT_PET:
                # needed for whale
                logging.debug(f"Fainting pet {trigger.pet}")
                self.apply_trigger(Trigger(TriggerType.PET_FAINTED, trigger.pet))

            elif trigger.type is TriggerType.REDUCE_HEALTH:
                # needed for skunk
                logging.debug(f"Reducing health {trigger.pet} {trigger.health_ratio}")
                trigger.pet.toughness = math.floor(trigger.pet.toughness * (1 - trigger.health_ratio))
                if trigger.pet.toughness == 0:
                    self.apply_trigger(Trigger(TriggerType.PET_FAINTED, trigger.pet))

            else:
                self.event_queue.extend([
                    (triggered_pet, new_trigger) for new_trigger
                    in triggered_pet.apply_trigger(trigger, my_team, other_team)])
