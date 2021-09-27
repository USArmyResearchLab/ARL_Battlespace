from src.GameModule import GameClass
from src.StateModule import StateClass

class CaptureFlag(GameClass):
    """
    Example _Capture the flag game_
    """
    def __init__(self, Agents):
        GameClass.__init__(self,Agents)
        pass

    def resolveActions(self, State, Changes):
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
        UnitChanges = defaultdict(Set)

        for (UnitID, NewUnit) in ValidChanges:
            UnitChanges[UnitID].add(NewUnit)

        # Consolidate the results from the various actions
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) > 1:
                # If any change leads to a removal of a unit it takes precedence
                # and it is removed from the state
                for Unit1 in UnitChanges[UnitID]:
                    if Unit1 is None:
                        State.Units[UnitID].Health = 0
                        UnitChanges.pop(UnitID)
                        break
                    elif State.Units[UnitID].Health == 0:
                        UnitChanges.pop(UnitID)
        # Update all units
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) > 1:
                State.Units[UnitID] = UnitChanges[UnitID].pop()

        RemoveUnits = set()
        # If two units overlap, they are destroyed.
        for UnitID1, Unit1 in State.Units.items():
            for UnitID2, Unit2 in State.Units.items():
                if areOverlapped(Unit1,Unit2):
                    RemoveUnits.add(UnitID1)
                    RemoveUnits.add(UnitID2)
        # Now update all units
        for UnitID in RemoveUnits:
            State.Units[UnitID].Health = 0
        return State

    def continueGame(self,StateClass):
        """
        Decide whether the game has reached its conclusion.

        Parameters
        ----------
        State : FlaggedStateClass
            A `StateClass` that has the attribute `Flags: dict`

        Returns
        -------
        bool

        """
        for Agent in self.Agents:
            if State.Flags[Agent.ID] != Agent.ID:
                return False
        return True

    def play(self, StateClass):
        R = GameClass.play(self, State)
        LastState = R[0]
        for Agent in self.Agents:
            if LastState.Flags[Agent.ID] != Agent.ID:
                print("Agent "+str(Agent.ID)+" lost the game")
        return R

    def correctObservation(self, Observer, Unit, ObservedUnit):
        # do something in a specific game
        if Unit.Health == 0:
            return None
        return ObservedUnit
