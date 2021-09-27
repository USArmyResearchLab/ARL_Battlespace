# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 09:49:47 2020

@author: james.z.hare
"""

from src.UnitModule import UnitClass, advance
from copy import deepcopy
import math

class ProjectileClass(UnitClass):
    """
    The Projectile Class
    
    This is a subclass to the UnitClass

    Virtual Functions
    -----------------
    - `__copy__()` to make shallow copies
    - `__deepcopy__(memo)` to make deep copies
    - `possibleActions(State)` to identify legal actions
    - `observe(Unit)` to observe units located within VisibleRange
    - `overlaps(Unit)` to identify if the unit overlaps with another unit
    - `execute(Action, State)` to execute the action
    

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
    RemaingLifetime:
        int that defines the total number of turns until the unit is dead

    """
    
    def __init__(self, ID, Owner, Health, RemainingLifetime=math.inf):
        UnitClass.__init__(self, ID, Owner, Health, Extent=(1,1))
        self.Actions = { "advance": lambda x: advance(self, x) }
        self.ActionOptions = ( ( "advance", ), )
        self.Attack = None
        self.RemainingLifetime = RemainingLifetime

    def __copy__(self):
        Duplicate = ProjectileClass(self.ID, self.Owner, self.Health)
        Duplicate.Position = self.Position
        Duplicate.Orientation = self.Orientation
        Duplicate.Attack = self.Attack
        Duplicate.RemainingLifetime = self.RemainingLifetime
        return Duplicate

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = ProjectileClass(deepcopy(self.ID, memo), deepcopy(self.Owner ,memo), deepcopy(self.Health, memo))
        Duplicate.Position = deepcopy(self.Position, memo)
        Duplicate.Orientation = deepcopy(self.Orientation, memo)
        Duplicate.Attack = deepcopy(self.Attack, memo)
        Duplicate.RemainingLifetime = deepcopy(self.RemainingLifetime, memo)
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
    
    def execute(self, Actions, State):
        """
        Execute `Actions` on `State`.

        Parameters
        ----------
        Actions : list[str]
            A set of actions to be performed on `State`.
        State : StateClass
            State on which to inflict actions.

        Returns
        -------
        Changes : list
            Resulting state of executed `Actions`.

        """
        NewState = deepcopy(State)
        Changes = []
        for Action in Actions:
            ActionResult = self.Actions[Action](NewState)
            ActionResult[1].RemainingLifetime -= 1
            if isinstance(ActionResult, list):
                Changes += ActionResult
            else:
                Changes.append(ActionResult)
        return Changes

# Will be used as the projectile for the missile launcher unit
class MissileClass(ProjectileClass):
    def __init__(self, ID, Owner, Position, Life=1):
        ProjectileClass.__init__(self, ID, Owner, Positon=Position, Life=Life)