# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 15:40:50 2020

@author: james.z.hare
"""
from src.UnitTypes.AirUnitModule import AirUnitClass
from src.UnitTypes.ProjectileModule import ProjectileClass
import math

class AirplaneClass(AirUnitClass):
    """
    The Airplane Class
    
    This is a subclass of the AirUnitClass, which is a subclass to the UnitClass

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
    
    def __init__(self, ID, Owner, Health, Position=None, Orientation=None, ShotRange=math.inf, VisibleRange=1, AdvanceRange=2):
        AirUnitClass.__init__(self, ID, Owner, Health, VisibleRange=VisibleRange, Position=Position, 
                                 Orientation=Orientation, AdvanceRange=AdvanceRange, ShotRange=ShotRange)
        Actions = {"shoot"  : self.shoot,
                   "bomb"   : self.bomb
                   }
        self.Actions.update(Actions)  # This here includes all default actions of defined by `AirUnitClass`
        self.ActionOptions = ( tuple(self.Actions.keys()), )
        
    def __copy__(self):
        NewUnit = AirplaneClass(self.ID, self.Owner, self.Health, Position=self.Position, Orientation=self.Orientation, 
                               VisibleRange=self.VisibleRange, AdvanceRange=self.AdvanceRange)
        NewUnit.Extent = self.Extent
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

    def bomb(self, State):
        """
        Adds a unit that will only descend.

        Arguments:
        ----------
        State: StateClass
            State upon which to act. Unused.

        Returns:
        --------
        (None, NewUnit: Projectile)
            A new unit is created and sent out
        """
        NewUnit = ProjectileClass(None, self.Owner, 1)
        NewUnit.Orientation = (0, 0, -1)
        NewUnit.Position = tuple(self.Position[i]+NewUnit.Orientation[i] for i in range(3))
        return (None, NewUnit)
        