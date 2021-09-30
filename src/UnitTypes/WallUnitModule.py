# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 15:53:55 2021

@author: james.z.hare
"""

from src.UnitModule import UnitClass
from copy import deepcopy

class WallClass(UnitClass):
    """
    The Wall Unit Class
    
    This is a subclass to the UnitClass and represents an obstacle that a unit cannot traverse through or overlap

    Virtual Functions
    -----------------
    - `__copy__()` to make shallow copies
    - `__deepcopy__(memo)` to make deep copies
    - `possibleActions(State)` to identify legal actions
    - `observe(Unit)` to observe units located within VisibleRange
    - `overlaps(Unit)` to identify if the unit overlaps with another unit

    Attributes
    ----------
    ID:
        a unique identifier of this unit
    Owner:
        the player the unit belongs to
    Extent:
        the space occupied by unit
    Health:
        the health of the unit
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

    """
    def __init__(self, ID, Owner, Health, Position, Orientation=None):
        UnitClass.__init__(self, ID, Owner, Health, Position=Position, Extent=(1,1), Orientation=Orientation)
        self.ActionOptions = ( tuple(self.Actions.keys()), )
        self.Life = None
        self.Attack = None
        
    def __copy__(self):
        Duplicate = WallClass(self.ID,self.Owner,self.Health,self.Position)
        Duplicate.Orientation = self.Orientation
        Duplicate.Attack = self.Attack
        Duplicate.Life = self.Life
        return Duplicate

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = WallClass(deepcopy(self.ID, memo), deepcopy(self.Owner,memo), deepcopy(self.Health,memo), deepcopy(self.Position,memo))
        Duplicate.Orientation = deepcopy(self.Orientation, memo)
        Duplicate.Attack = deepcopy(self.Attack, memo)
        Duplicate.Life = deepcopy(self.Life, memo)
        memo[self] = Duplicate
        return Duplicate
    
    def possibleActions(self, State):
        """
        Identifies the set of feasible actions given the board size and position of the unit

        Parameters
        ----------
        State: StateClass

        Returns
        -------
        TrueActions: list[str]
            A list of the feasible actions
        """
        return self.ActionOptions

    def observe(self, Unit):
        if Unit.ID == self.ID:
           return Unit
        return None

    def overlaps(self, Unit):
        MyOccupiedSpace = set([ (self.Position[0]+x, self.Position[1]+y, self.Position[2]) for x in range(self.Extent[0]) for y in range(self.Extent[1]) ])
        #print(Unit)
        TheirOccupiedSpace = set([ (Unit.Position[0]+x, Unit.Position[1]+y, Unit.Position[2]) for x in range(Unit.Extent[0]) for y in range(Unit.Extent[1]) ])
        return len(MyOccupiedSpace.intersection(TheirOccupiedSpace))>0
        
