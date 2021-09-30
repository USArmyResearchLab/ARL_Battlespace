# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 10:26:58 2020

@author: james.z.hare
"""

from src.StateModule import StateClass
from src.UnitTypes.SoldierModule import SoldierClass
from src.UnitTypes.TruckModule import TruckClass
from src.UnitTypes.TankModule import TankClass
#from MissileLauncherModule import MissileLauncherClass
from src.UnitTypes.AirplaneModule import AirplaneClass

class TeamStateClass(StateClass):
    """
    State of game which includes a captured flag.
    """
    def __init__(self):
        StateClass.__init__(self)
        self.FlagOwner = None
        self.FlagPosition = None
        self.BoardSize = None
        self.GroundOnlyUnits = ( SoldierClass, TruckClass, TankClass, ) # MissileLauncherClass, )
        self.AirOnlyUnits = ( AirplaneClass, )

    def isLegalChange(self, Change):
        Unit = Change[1]
        if Unit is None:
            return True
        # Check if the unit is a ground only unit, i.e., can only have a position on the lowest level of the board
        if any([ isinstance(Unit,Type) for Type in self.GroundOnlyUnits ]):
            if any([ Unit.Position[i] >= self.BoardSize[i] or Unit.Position[i] < 0 for i in range(2) ]):
                return False
            if Unit.Position[2] != 0:
                return False
        # Check if the unit is an air only unit, i.e., cannot have a position on the lowest level of the board
        elif any([ isinstance(Unit,Type) for Type in self.AirOnlyUnits ]):
            if any([ (Unit.Position[i] >= self.BoardSize[i] or Unit.Position[i] < 0) for i in range(2) ]):
                return False
            if Unit.Position[2] <1 or Unit.Position[2] >= self.BoardSize[2]:
                return False                   
        # The unit can move freely amongst the board
        else:
            if any([ Unit.Position[i] >= self.BoardSize[i] for i in range(3) ]):
                return False
            if any([ Unit.Position[i] <0 for i in range(3) ]):
                return False
        return True

    def isLegalAction(self, Changes):
        if not Changes is None:
            if isinstance(Changes, list):
                return all([ self.isLegalChange(Change) for Change in Changes ])
            else:
                return self.isLegalChange(Changes)
        return True
