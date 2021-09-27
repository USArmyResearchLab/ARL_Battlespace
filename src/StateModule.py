# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:06:28 2020

@author: berend
"""

from collections import defaultdict, Set

class StateClass(object):
    """
    Parent class of all States

    Attributes
    ----------
    Units
        A dictionary of of Unit IDs pointing to Units
    Players
        None for no players or a set of player IDs
    BoardSize
        A tuple describing the extension of the board

    """
    def __init__(self):
        """
        Constructor
        """
        self.Units   = {}
        self.Players = None
        self.BoardSize = (10,10)

    def __str__(self):
        ReturnString = str(self.__class__.__name__) + ": \n"
        ReturnString+= "   BoardSize = "+str(self.BoardSize)+"\n"
        for UnitID in self.Units.keys():
            ReturnString += "   Unit "+str(UnitID)+" "+str(self.Units[UnitID])
        return ReturnString

    def isLegal(self):
        """
        Decides whether I am a legal game state.

        Returns
        -------
        bool.

        """
        for UnitID1 in self.Units.keys():
            Unit1 = self.Units[UnitID1]
            if Unit1.ID != UnitID1:
                return False
            for UnitID2 in self.Units.keys():
                Unit2 = self.Units[UnitID2]
                if UnitID1 != UnitID2 and self.contradictory(Unit1, Unit2):
                    return False
        return True

    def newUnitID(self):
        UnitIDs = set([x for x in self.Units.keys()])
        MaxID = max(UnitIDs)
        return MaxID + 1
