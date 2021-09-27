# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:06:28 2020

@author: berend.c.rinderspacher.civ@mail.mil
"""

from src.StateModule import StateClass
from src.UnitTypes.ExampleUnit import ExampleUnit, ProjectileClass, FlagClass

class ExampleStateClass(StateClass):
    """
    State of game which includes a captured flag.
    """
    def __init__(self):
        StateClass.__init__(self)
        self.FlagOwner = None
        self.FlagPosition = None
        self.BoardSize = None
        self.AllowedUnits = [ ExampleUnit, ProjectileClass, FlagClass ]

    def isLegalChange(self, Change):
        Unit = Change[1]
        if Unit is None:
            return True
        if not any([ isinstance(Unit, AllowedType) for AllowedType in self.AllowedUnits ]):
            return False
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
