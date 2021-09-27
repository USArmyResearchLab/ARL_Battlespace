#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 20:43:46 2020

@author: berend
"""

from copy import deepcopy
from math import cos, sin
import numpy as np
#from ProjectileModule import ProjectileClass

import warnings

class UnitClass(object):
    """
    Parent class for all unit types.

    This is an abstract class. For proper use in a game, units must define

    Virtual Functions
    -----------------
    - `observe(Unit: UnitClass): Union{Tuple{ID,UnitClass},None}` which returns a unit with observed properties or `None` if nothing is observed.
    - `__copy__()` to make shallow copies
    - `__deepcopy__(memo)` to make deep copies

    Attributes
    ----------
    ID:
        a unique identifier of this unit
    Owner:
        the player the unit belongs to
    Extent:
        the space occupied by unit
    Position:
        location of unit
    Orientation:
        as the name says
    VisibleRange:
        how far the unit can observe
    VisibleUnits:
        list of other players unit in visible range
    Actions: dict
        dictionary of actions common accross all units
    ActionOptions:
        list of list of action options.
    Attack:
        Flag for attack options.
    Health:
        measure of operability.

    """

    def __init__(self, ID, Owner, Health = 1, Extent=None, Position=None, Orientation=None, VisibleRange=0, VisibleUnits=None):
        self.ID            = ID
        self.Owner         = Owner
        self.Extent        = Extent
        self.Position      = Position
        self.Orientation   = Orientation
        self.VisibleRange  = VisibleRange
        self.VisibleUnits  = VisibleUnits
        self.Actions       = {"doNothing" : noAction}
        self.DefaultActions = None
        self.ActionOptions  = None
        self.Attack         = None
        self.Health         = Health

    def __str__(self):
        ReturnString  = str(self.__class__.__name__)+"\n"
        for Name in self.__dict__.keys():
            ReturnString += "   "+Name+": "+str(self.__dict__[Name])+"\n"
        return ReturnString

    def __repr__(self):
        ReturnString = repr(self.__class__) + "("
        for Name in self.__dict__.keys():
            ReturnString += Name+'='+repr(self.__dict__[Name])+","
        return ReturnString + ")"

    def __copy__(self):
        """
        Shallow copy
        """
        raise NotImplementedError(str(self.__class__.__name__) + " <: UnitClass is an abstract class that requires `__copy__` to be defined by derived specific classes")

    def __deepcopy__(self, memo):
        """
        Deep copy
        """
        raise NotImplementedError(self.__class__.__name__+" <: UnitClass is an abstract class that requires `__deepcopy__` to be defined by derived specific classes")

    def observe(self, Unit):
        """
        Simply report back what of `Unit` is observed by this UnitClass instance.
        """
        raise NotImplementedError("UnitClass is an abstract class that requires `observe` to be defined by derived classes")
    
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
        if self.Health == 0:
            return tuple([ "doNothing" ])
        
        TrueActions = []
        for Action in self.Actions.keys():
            ActionResult = self.Actions[Action](State)
            if State.isLegalAction(ActionResult):
                TrueActions.append(Action)
        ActionOptions =tuple([ tuple([Option for Option in Options if Option in TrueActions]) for Options in self.ActionOptions ])
        return ActionOptions


    def executeDefaults(self, State):
        """
        Execute `DefaultActions` on `State`.

        Parameters
        ----------
        State : StateClass
            State on which to inflict actions.

        Returns
        -------
        NewState : StateClass
            Resulting state of executed `Actions`.

        """
        return self.execute(self.DefaultActions, State)

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
            if isinstance(ActionResult, list):
                Changes += ActionResult
            else:
                Changes.append(ActionResult)
        return Changes

def noAction(State):
    """
    Do nothing option.

    Arguments
    ---------
    State : StateClass
        governing state, ignored.

    Returns
    -------
    None

    """
    return None

def turn(Unit: UnitClass, State, N):
    """
    Turn the unit by N degrees.

    Arguments
    ---------
    Unit : UnitClass
        Unit to turn
    State
        governing state, ignored
    N
        Degrees of rotation

    Returns
    -------
    ID of the turned unit and the rotated unit as a tuple.

    """
    Orientation = [ Unit.Orientation[0]*cos(-N) - Unit.Orientation[1]*sin(-N), Unit.Orientation[0]*sin(-N) + Unit.Orientation[1]*cos(-N), Unit.Orientation[2] ]
    for i in range(2):
        if abs(Orientation[i]) > 0.001:
            Orientation[i] = Orientation[i]/abs(Orientation[i])
        else:
            Orientation[i] = 0
    NewUnit = deepcopy(Unit)
    NewUnit.Attack = None
    NewUnit.Orientation = tuple(Orientation)
    return (Unit.ID, NewUnit)

def elevate(Unit: UnitClass, State, Levels):
    """
    Change elevation.

    Arguments:
    ----------
    State: StateClass
        state upon which to act, unused here
    Levels: int
        How many levels to go up or down

    Returns:
    --------
    (ID, NewUnit : ExampleUnit)
        This unit's ID and a new ExampleUnit with updated elevation
    """
    Elevation = Unit.Position[2] + Levels
    Position = [ x for x in Unit.Position ]
    Position[2] = Elevation
    NewUnit = deepcopy(Unit)
    NewUnit.Attack = None
    NewUnit.Position = tuple(Position)
    return (Unit.ID, NewUnit)

def advance(Unit: UnitClass, State):
    """
    Advance the unit by 1 in the current orientation

    Arguments:
    ----------
    Unit: UnitClass
        Unit to advance
    State: StateClass
        State upon which to act. Unused.

    Returns:
    --------
    (Unit.ID, NewUnit)
        A new unit is created with the new position and same id
    """
    Position = [x for x in Unit.Position]
    for i in range(3):
        Position[i] += Unit.Orientation[i]
    NewUnit = deepcopy(Unit)
    NewUnit.Attack = None
    NewUnit.Position = tuple(Position)
    return (Unit.ID, NewUnit)

def advanceN(Unit: UnitClass, State, N):
    """
    Advances by N in the direction of the current orientation.

    Arguments:
    ----------
    Unit: UnitClass
        Unit to advance
    State: StateClass
        State upon which to act. Unused.
    N: int
        Number of cells the unit will advance

    Returns:
    --------
    (Unit.ID, NewUnit)
        A new unit is created with the new position and same id
    """
    Position = [x for x in Unit.Position]
    for i in range(3):
        Position[i] += Unit.Orientation[i]*N
    NewUnit = deepcopy(Unit)
    NewUnit.Attack = None
    NewUnit.Position = tuple(Position)
    return (Unit.ID, NewUnit)

def advanceNM(Unit: UnitClass, State, N, M):
    """
    Advance to the position (N,M) in the (X,Y) plane

    Arguments:
    ----------
    Unit: UnitClass
        Unit to advance
    State: StateClass
        State upon which to act. Unused.
    N: int
        X position
    M: int
        Y position

    Returns:
    --------
    (Unit.ID, NewUnit)
        A new unit is created with the new position and same id
    """
    Position = [x for x in Unit.Position]
    Position = ( Position[0]+M, Position[1]+N, Position[2] )
    NewUnit = deepcopy(Unit)
    NewUnit.Position = Position
    NewUnit.Attack = None
        
    return (Unit.ID, NewUnit)

def ram(Unit: UnitClass, State):
    """
    Advances by one destroying the target.
    Action only exists to exemplify mulitple unit modifications in a single action.

    Arguments:
    ----------
    Unit: UnitClass
        Unit to advance and ram
    State: StateClass
        State upon which to act. Unused.

    Returns:
    --------
    (Unit, NewUnit)
        A new unit is created with the new position.
    """
    NewUnit = advance(Unit,State)[1]
    NewUnit.Attack = 1

    return (Unit.ID, NewUnit)
