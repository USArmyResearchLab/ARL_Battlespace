from src.GameModule import GameClass
# from StateModule import StateClass
from collections import defaultdict, Set
from src.StateTypes.ExampleState import ExampleStateClass
from src.UnitTypes.ExampleUnit import ExampleUnit
from src.UnitTypes.ExampleUnit import FlagClass

def first(D):
    for key in D.keys():
       return D[key]
    return None

class CaptureFlag(GameClass):
    """
    Example _Capture the flag game_
    """

    def __init__(self, Agents):
        GameClass.__init__(self, Agents)
        self.FlagCapturers = ( ExampleUnit, )
        self.PrintOn = False

    def resolveActions(self, State: ExampleStateClass, Changes):
        """
        Resolve contradictory actions and update.

        Parameters
        ----------
        State : StateClass
            State on which to resolve the actions.
        Changes : list
            List of tuples `(UnitID, Unit: UnitClass)`.

        Returns
        -------
        State.

        """
        ValidChanges = [x for x in Changes if x is not None]
        UnitChanges = defaultdict(set)

        for (UnitID, NewUnit) in ValidChanges:
            if UnitID is None:
                UnitID = State.newUnitID()
                NewUnit.ID = UnitID
                if self.PrintOn:
                    print("Gave Agent ID = ", NewUnit.Owner, " a new unit of type", type(NewUnit)," a new ID =", UnitID, " located at ", NewUnit.Position, " with Orientation ", NewUnit.Orientation, ".\n")
            UnitChanges[UnitID].add(NewUnit)

        # Consolidate the results from the various actions
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) >= 1:
                # If any change leads to a removal of a unit it takes precedence
                # and it is removed from the state
                for Unit1 in UnitChanges[UnitID]:
                    if Unit1 is None:
                        if self.PrintOn:
                            print("removing unit ",State.Units[UnitID]," with ",UnitID," because it was destroyed\n")
                        State.Units.pop(UnitID)
                        UnitChanges.pop(UnitID)
                        break

        # Update all units
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) >= 1:
                Unit = UnitChanges[UnitID].pop()
                if self.PrintOn:
                    print("Agent ID = ", Unit.Owner, " changed Unit ID =",UnitID," position to ",Unit.Position, " and orientation to ", Unit.Orientation, ".\n")
                State.Units[UnitID] = Unit # Only one version will be used.

        RemoveUnits = set()
        # If a unit goes out of bounds, destroy it
        for UnitID, Unit in State.Units.items():
            if any([ Unit.Position[i] >= State.BoardSize[i] for i in range(3) ]):
                if self.PrintOn:
                    print("removing Unit ID = ", UnitID, " of type ", type(Unit)," for being outside board (> ",State.BoardSize,")\n")
                RemoveUnits.add(UnitID)
            if any([ Unit.Position[i] <0 for i in range(3) ]):
                if self.PrintOn:
                    print("removing Unit ID = ", UnitID, " of type ", type(Unit)," for being outside board (< 0)\n")
                RemoveUnits.add(UnitID)

        while len(RemoveUnits) > 0:
            State.Units.pop(RemoveUnits.pop())

        # If two units overlap, they are destroyed.
        for UnitID1, Unit1 in State.Units.items():
            for UnitID2, Unit2 in State.Units.items():
                if Unit1 != Unit2 and Unit1.overlaps(Unit2):
                    if Unit1.Attack == Unit2.Attack: # Both units are either attacking or not
                        RemoveUnits.add(UnitID1)
                        RemoveUnits.add(UnitID2)
                        if self.PrintOn:
                            print("Removing Units with IDs ",UnitID1, " and ", UnitID2," for overlapping.\n")
                    elif Unit1.Attack == 1 and Unit2.Attack == None: # Unit1 is attacking while Unit2 is not
                        RemoveUnits.add(UnitID2)
                        if self.PrintOn:
                            print("Removing Unit with ID = ",UnitID2, " since it was attacked by Unit ID = ", UnitID1,".\n")
                    else:                                           # Unit2 is attacking while Unit1 is not
                        RemoveUnits.add(UnitID1)
                        if self.PrintOn:
                            print("Removing Unit with ID = ",UnitID1, " since it was attacked by Unit ID = ", UnitID2,".\n")


        # Now remove relevant units
        for UnitID in RemoveUnits:
            State.Units.pop(UnitID)

        for Unit in State.Units.values():
            if Unit.Position == State.FlagPosition and any([isinstance(Unit,T) for T in self.FlagCapturers]):
                State.FlagOwner = Unit.Owner
                break # only one unit can occupy a space.
        return State

    def continueGame(self,State: ExampleStateClass):
        """
        Decide whether the game has reached its conclusion.

        Parameters
        ----------
        State : ExampleStateClass
            A `StateClass` that has the attribute `Flags: dict`

        Returns
        -------
        bool
            True: Continue game, False: stop game

        """
        if self.PrintOn:
            print("Flag: "+str(State.FlagOwner)+" # Units = "+str(len(State.Units))+" # keys "+str(State.Units.keys()))
        return ( State.FlagOwner is None ) and ( len(State.Units) > 0 ) and ( len(State.Units.keys()) > 1 ) and len(set([Unit.Owner for Unit in State.Units.values() if isinstance(Unit,ExampleUnit)]))>1

    def play(self, State: ExampleStateClass):
        R = GameClass.play(self, State)
        LastState = R[0]
        Winner = None
        if len(LastState.Units) == 0:
            if self.PrintOn:
                print("Mutual desctruction")
        elif LastState.FlagOwner != None:
            Winner = LastState.FlagOwner
            if self.PrintOn:
                print("Agent ",LastState.FlagOwner," won the game.")
        else:
            Player = first(LastState.Units).Owner
            Winner = Player
            if self.PrintOn:
                print("Agent %s won the game by elimination." %(Player))
        return R, Winner

    def correctObservation(self, Observer, Unit, ObservedUnit):
        if isinstance(Unit, FlagClass):
            return Unit.__copy__()
        return ObservedUnit
