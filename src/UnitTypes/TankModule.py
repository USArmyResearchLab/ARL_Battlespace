# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 11:45:35 2020

@author: james.z.hare
"""

from src.UnitTypes.GroundUnitModule import GroundUnitClass
import math


class TankClass(GroundUnitClass):
    """
    The Tank Class
    
    This is a subclass of the GroundUnitClass, which is a subclass to the UnitClass

    Virtual Functions
    -----------------
    - `__copy__()` to make shallow copies
    - `__deepcopy__(memo)` to make deep copies

    Attributes
    ----------
    ID:
        a unique identifier of this unit
    Owner:
        the player the unit belongs to
    Health:
        the health of the unit
    Extent:
        the space occupied by unit
    Position:
        location of unit
    Orientation:
        as the name says
    VisibleRange:
        how far the unit can observe
    Actions: dict
        dictionary of actions common accross all units
    ActionOptions:
        list of list of action options.
    Attack:
        int that defines whether the unit is attacking in an advance action
    AdvanceRange:
        int that defines how many total spaces the unit can move
    ShotRange:
        int that defines the number of cells the projectile can travel before dying

    """

    def __init__(self, ID, Owner, Health, Position=None, Orientation=None, ShotRange=math.inf, VisibleRange=1, AdvanceRange=1):
        GroundUnitClass.__init__(self, ID, Owner, Health, VisibleRange=VisibleRange, Position=Position, 
                                 Orientation=Orientation, AdvanceRange=AdvanceRange, ShotRange=ShotRange)
        
    def __copy__(self):
        NewUnit = TankClass(self.ID, self.Owner, self.Health, Position=self.Position, Orientation=self.Orientation)
        NewUnit.Extent = self.Extent
        NewUnit.VisibleRange = self.VisibleRange
        NewUnit.Attack = self.Attack
        NewUnit.ShotRange = self.ShotRange
        return NewUnit

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = self.__copy__()
        memo[self] = Duplicate
        return Duplicate