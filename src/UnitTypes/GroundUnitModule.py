# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 10:51:01 2020

@author: james.z.hare
"""

from src.UnitModule import UnitClass, turn, advanceN, ram
from src.UnitTypes.ProjectileModule import ProjectileClass
from math import pi
from copy import deepcopy
import math


class GroundUnitClass(UnitClass):
    """
    The Ground Unit Class
    
    This is a subclass to the UnitClass

    Virtual Functions
    -----------------
    - `__copy__()` to make shallow copies
    - `__deepcopy__(memo)` to make deep copies
    - `possibleActions(State)` to identify legal actions
    - `observe(Unit)` to observe units located within VisibleRange
    - `overlaps(Unit)` to identify if the unit overlaps with another unit
    - `shoot(State)` to shoot a projectile in the current orientation
    - `ram(State)` to advance and attack 
    - `advanceN(State)` to advance N spaced in the current orientation

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

    def __init__(self, ID, Owner, Health, Position=None, Orientation=None, VisibleRange=1, AdvanceRange=1, ShotRange=math.inf):
        UnitClass.__init__(self, ID, Owner, Health, Extent=(1, 1), VisibleRange=VisibleRange, Position=Position, Orientation=Orientation)
        Actions = { "turn"+str(N): (lambda x, n=N: turn(self, x, n/180*pi))  for N in range(-135,180+1,45) }
        Actions.update({ "advance"+str(N): (lambda x, n=N: advanceN(self, x, n)) 
                    for N in range(1,AdvanceRange+1) })
        Actions.update({
                        "shoot"  : self.shoot,
                        "ram"    : lambda x: ram(self, x)
                       })
        self.Actions.update(Actions)  # This here includes the default action of doNothing
        self.ActionOptions = ( tuple(self.Actions.keys()), )
        self.Attack = None
        self.ShotRange = ShotRange

    def __copy__(self):
        NewUnit = GroundUnitClass(self.ID, self.Owner, self.Health, Position=self.Position, Orientation=self.Orientation)
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

    def observe(self, Unit: UnitClass):
        """
        Simply report back what of `Unit` is observed by this ExampleUnit.
        This basic representative has no orientation or position, unless the unit is owned by this unit's owner.
        Extent is ignored.
        This unit has infinite vision in the z direction.

        Arguments:
        ----------
        Unit: UnitClass
            Unit to be observed.

        Returns:
        -------
        NewUnit: UnitClass
            What we saw of that unit.
        """
        if Unit.Owner == self.Owner:
            return Unit
        ObservedPositions = [ (self.Position[0]+x, self.Position[1]+y) for x in range(-self.VisibleRange,self.VisibleRange+1) for y in range(-self.VisibleRange,self.VisibleRange+1)]
        X0, Y0 = Unit.Position[0:2]
        if not (X0,Y0) in ObservedPositions:
            return None

        # Retain the unit ID for the game state
        # But forget who owns it.
        NewUnit = UnitClass(Unit.ID, None, None)
        NewUnit.Extent = deepcopy(Unit.Extent)
        NewUnit.Position = deepcopy(Unit.Position)
        return NewUnit

    def overlaps(self,Unit):
        MyOccupiedSpace = set([ (self.Position[0]+x, self.Position[1]+y, self.Position[2]) for x in range(self.Extent[0]) for y in range(self.Extent[1]) ])
        # print(Unit)
        TheirOccupiedSpace = set([ (Unit.Position[0]+x, Unit.Position[1]+y, Unit.Position[2]) for x in range(Unit.Extent[0]) for y in range(Unit.Extent[1]) ])
        return len(MyOccupiedSpace.intersection(TheirOccupiedSpace))>0

    def shoot(self, State):
        """
        Adds a unit that will follow only the current orientation maintaining level.

        Arguments:
        ----------
        State: StateClass
            State upon which to act. Unused.

        Returns:
        --------
        (None, NewUnit: Projectile)
            A new unit is created and sent out
        """
        NewUnit = ProjectileClass(None, self.Owner, 1, RemainingLifetime=self.ShotRange)
        NewUnit.Orientation = (self.Orientation[0], self.Orientation[1], 0)
        NewUnit.Position = tuple(self.Position[i]+NewUnit.Orientation[i] for i in range(3))
        return (None, NewUnit)
    
    def noAction(self, State):
        """
        Do nothing option.
    
        Parameters
        ----------
        State : StateClass
            governing state, ignored.
    
        Returns
        -------
        None
    
        """
        self.Attack = None
        return None