# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:13:28 2020

@author: berend.c.rinderspacher.civ@mail.mil
"""

from src.UnitModule import UnitClass, turn, elevate, advance, ram
from math import pi
from copy import deepcopy


class ExampleUnit(UnitClass):
    """
    `ExampleUnit` is a template for creating `UnitClass` objects for use in
    a game of BattleSpace

    """

    def __init__(self, ID, Owner, Position=None, Orientation=None):
        UnitClass.__init__(self, ID, Owner, Extent=(1, 1), VisibleRange=1, Position=Position, Orientation=Orientation)
        Actions = { "turn"+str(N): (lambda x, n=N: turn(self, x, n/180*pi))  for N in [45,-45] }
        Actions.update({
                        "advance": lambda x: advance(self,x),
                        "ascend" : lambda x: elevate(self, x, 1),
                        "descend": lambda x: elevate(self, x, -1),
                        "shoot"  : self.shoot,
                        "bomb"   : self.bomb,
                        "ram"    : self.ram
                       })
        self.Actions.update(Actions)  # This here includes the default action of doNothing
        self.ActionOptions = ( tuple(self.Actions.keys()), )
        self.Attack = None

    def __copy__(self):
        NewUnit = ExampleUnit(self.ID, self.Owner, Position=self.Position, Orientation=self.Orientation)
        NewUnit.Extent = self.Extent
        NewUnit.VisibleRange = self.VisibleRange
        NewUnit.Attack = self.Attack
        return NewUnit

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = self.__copy__()
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

        TrueActions = []
        for Action in self.Actions.keys():
            ActionResult = self.Actions[Action](State)
            if State.isLegalAction(ActionResult):
                TrueActions.append(Action)
        ActionOptions =tuple([ tuple([Option for Option in Options if Option in TrueActions]) for Options in self.ActionOptions ])
        return ActionOptions

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
        NewUnit = UnitClass(Unit.ID, None)
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
        NewUnit = ProjectileClass(None, self.Owner)
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
        NewUnit = ProjectileClass(None, self.Owner)
        NewUnit.Orientation = (0, 0, -1)
        NewUnit.Position = tuple(self.Position[i]+NewUnit.Orientation[i] for i in range(3))
        return (None, NewUnit)

    def ram(self, State):
        """
        Advances by one destroying the target.
        Action only exists to exemplify mulitple unit modifications in a single action.

        Arguments:
        ----------
        State: StateClass
            State upon which to act. Unused.

        Returns:
        --------
        (None, NewUnit: Projectile)
            A new unit is created and sent out
        """
        NewUnit = advance(self,State)[1]
        NewUnit.Attack = 1
#        Result = [(self.ID, MyUnit)]
#        for Unit in State.Units.values():
#            if Unit.Position == MyUnit.Position:
#                TheirUnitID = Unit.ID
#                Result.append( ( TheirUnitID, None ) )
#                break

        return (self.ID, NewUnit)


class ProjectileClass(UnitClass):
    def __init__(self, ID, Owner):
        UnitClass.__init__(self, ID, Owner, Extent=(1,1))
        self.Actions = { "ram": lambda x: ram(self, x) }
        self.ActionOptions = ( ( "ram", ), )
        self.Attack = 1

    def __copy__(self):
        Duplicate = ProjectileClass(self.ID,self.Owner)
        Duplicate.Position = self.Position
        Duplicate.Orientation = self.Orientation
        Duplicate.Attack = self.Attack
        return Duplicate

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = ProjectileClass(deepcopy(self.ID, memo), deepcopy(self.Owner,memo))
        Duplicate.Position = deepcopy(self.Position, memo)
        Duplicate.Orientation = deepcopy(self.Orientation, memo)
        Duplicate.Attack = deepcopy(self.Attack, memo)
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
        ActionString = self.Actions.keys()
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


class FlagClass(UnitClass):

    def __init__(self, ID=None, Owner=None, Health=None, Position=None, Orientation=None):
        UnitClass.__init__(self, ID, Owner, Health, Extent=(1, 1), VisibleRange=0, Position=Position, Orientation=Orientation)
        self.ActionOptions = ( ( "doNothing", ), )

    def __copy__(self):
        NewUnit = FlagClass(self.ID, self.Owner, self.Health, Position=self.Position, Orientation=self.Orientation)
        NewUnit.Extent = self.Extent
        NewUnit.VisibleRange = self.VisibleRange
        NewUnit.Attack = self.Attack
        return NewUnit

    def __deepcopy__(self, memo):
        Default = None
        Exists = memo.get(self, Default)
        if Exists is not Default:
            return Exists
        Duplicate = self.__copy__()
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
        return None

    def overlaps(self, Unit):
        MyOccupiedSpace = set([ (self.Position[0]+x, self.Position[1]+y, self.Position[2]) for x in range(self.Extent[0]) for y in range(self.Extent[1]) ])
        #print(Unit)
        TheirOccupiedSpace = set([ (Unit.Position[0]+x, Unit.Position[1]+y, Unit.Position[2]) for x in range(Unit.Extent[0]) for y in range(Unit.Extent[1]) ])
        return len(MyOccupiedSpace.intersection(TheirOccupiedSpace))>0
