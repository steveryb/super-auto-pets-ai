import pytest
from sap.pet import *


class TestPet:
    def test_takes_base_stats(self):
        pet = Pet("Test", "T", 1, 2)
        assert pet.power == 1
        assert pet.toughness == 2
        assert pet.name == "Test"
        assert pet.symbol == "T"
