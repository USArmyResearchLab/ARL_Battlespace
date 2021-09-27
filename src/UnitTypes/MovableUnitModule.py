# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 13:46:12 2020

@author: james.z.hare
"""

from copy import deepcopy
from warnings import warn
from src.UnitModule import UnitClass

class MovableUnitClass(UnitClass):
    """
    Parent class for all movable unit types.
    
    ...
    
    Attributes
    ----------
    ID: int
        a unique identify of this unit
    Owner: str
        the payer the unit belongs to
    Extent: list[int]
        number of squares the unit occupies (width,length)
    Position: list[int]
        location of each square the unit occupies, front to back,  [(x,y)]
    Orientation: int
        angle unit is facing, North-0, East=90, South=180, West=270
    VisibleRange: int
        number of squares the unit can sense (currently in all directions)
    VisibleUnits: list[str]
        list of other players unit in visible range
    Actions: dic
        dictionary of actions common accross all units
    ActionOptions: list[str]
        list of actions
    TotalMovableSpaces: int
        Total number of spaces allowed to move in each direction
    
        
    Functions
    ---------
    Note that all function are current built for an extent = (1,1)
    
    
    """
    def __init__(self,ID,Owner):
        super().__init__(ID,Owner)
        self.Actions.update({
                                "moveRightOne": self.moveRightOne,
                                "moveLeftOne": self.moveLeftOne,
                                "moveForwardOne": self.moveForwardOne,
                                "moveBackwardOne": self.moveBackwardOne,
                                "rotateRight": self.rotateRight,
                                "rotateLeft": self.rotateLeft,
                                "rotate180": self.rotate180,
                                "rotateRightMoveForwardOne": self.rotateRightMoveForwardOne,
                                "rotateLeftMoveForwardOne": self.rotateLeftMoveForwardOne,
                                "moveForwardOneRotateRight": self.moveForwardOneRotateRight,
                                "moveForwardOneRotateLeft": self.moveForwardOneRotateLeft,
                            })
        self.ActionOptions= (self.Actions.keys(),)
        self.TotalMovableSpaces = 1
        
# Action definitions
    
    def moveRightOne(self,State):
        """
        Moves unit right one square and holds orientation

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with position one square to the right

        """
        Pos = self.Position
        if self.Orientation == 0:
            Pos = [self.Position[0]+1, self.Position[1]]
        elif self.Orientation == 90:
            Pos = [self.Position[0], self.Position[1]-1]
        elif self.Orientation == 180:
            Pos = [self.Position[0]-1, self.Position[1]]
        elif self.Orientation == 270:
            Pos = [self.Position[0], self.Position[1]+1]    
        else:
            warn('Warning: Unit Orientation is None')
        NewUnit = deepcopy(self)
        NewUnit.Position = Pos
        return (self.ID,NewUnit)
    
    def moveLeftOne(self,State):
        """
        Moves unit left one square and holds orientation

        Parameters
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position one square to the left

        """
        Pos = self.Position
        if self.Orientation == 0:
            Pos = [self.Position[0]-1, self.Position[1]]
        elif self.Orientation == 90:
            Pos = [self.Position[0], self.Position[1]+1]
        elif self.Orientation == 180:
            Pos = [self.Position[0]+1, self.Position[1]]
        elif self.Orientation == 270:
            Pos = [self.Position[0], self.Position[1]-1]    
        else:
            warn('Warning: Unit Orientation is None')
        NewUnit = deepcopy(self)
        NewUnit.Position = Pos
        return (self.ID,NewUnit)
    
    def moveForwardOne(self,State):
        """
        Moves unit forward one square and holds orientation

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position one square forward

        """
        Pos = self.Position
        if self.Orientation == 90:
            Pos = [self.Position[0]+1, self.Position[1]]
        elif self.Orientation == 180:
            Pos = [self.Position[0], self.Position[1]-1]
        elif self.Orientation == 270:
            Pos = [self.Position[0]-1, self.Position[1]]
        elif self.Orientation == 0:
            Pos = [self.Position[0], self.Position[1]+1]    
        else:
            warn('Warning: Unit Orientation is None')
        NewUnit = deepcopy(self)
        NewUnit.Position = Pos
        return (self.ID,NewUnit)
    
    def moveBackwardOne(self,State):
        """
        Moves unit backward one square and holds orientation

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position one square backward

        """
        Pos = self.Position
        if self.Orientation == 90:
            Pos = [self.Position[0]-1, self.Position[1]]
        elif self.Orientation == 180:
            Pos = [self.Position[0], self.Position[1]+1]
        elif self.Orientation == 270:
            Pos = [self.Position[0]+1, self.Position[1]]
        elif self.Orientation == 0:
            Pos = [self.Position[0], self.Position[1]-1]    
        else:
            warn('Warning: Unit Orientation is None')
        NewUnit = deepcopy(self)
        NewUnit.Position = Pos
        return (self.ID,NewUnit)
    
    def rotateRight(self,State):
        """
        Rotate unit 90 degrees to the right
            the pivot is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position rotated right 90 degrees

        """
        NewUnit = deepcopy(self)
        NewUnit.Orientation = (self.Orientation + 90)%360
        return (self.ID,NewUnit)
    
    def rotateLeft(self,State):
        """
        Rotate unit 90 degrees to the left
            the pivot is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position rotated left 90 degrees

        """
        NewUnit = deepcopy(self)
        NewUnit.Orientation = (self.Orientation + 270)%360
        return (self.ID,NewUnit)
    
    def rotate180(self,State):
        """
        Rotate unit 180 degrees
            the pivot is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position rotated 180 degrees

        """
        NewUnit = deepcopy(self)
        NewUnit.Orientation = (self.Orientation + 180)%360
        return (self.ID,NewUnit)
    
    def rotateRightMoveForwardOne(self,State):
        """
        Rotate unit right 90 degrees and then forward one square
            the pivot is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position rotated clockwise 90 degrees and forward one square

        """
        NewUnit = self.rotateRight(State)[2].moveForwardOne(State)
        return NewUnit
    
    def rotateLeftMoveForwardOne(self,State):
        """
        Rotate unit left 90 degrees and then forward one square
            the anchor of rotation is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position rotated 90 degrees left and forward one square

        """
        NewUnit = self.rotateLeft(State)[2].moveForwardOne(State)
        return NewUnit
    
    def moveForwardOneRotateRight(self,State):
        """
        Move unit forward one square and then rotate right 90 degrees
            the anchor of rotation is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position forward one square and rotated 90 degrees

        """
        NewUnit = self.moveForwardOne(State)[2].rotateRight(State)
        return NewUnit
    
    def moveForwardOneRotateLeft(self,State):
        """
        Move unit forward one square and then rotate left 90 degrees
            the anchor of rotation is based on the head of the unit

        Parameters
        ----------
        State : StateClass
            governing state, ignored.

        Returns
        -------
        ID: Any
            Unit to which update applies
        NewUnit: UnitClass
            Unit with unit position forward one square and rotated 270 degrees

        """
        NewUnit = self.moveForwardOne(State)[2].rotateLeft(State)
        return NewUnit
    
    
# Debugging
        
