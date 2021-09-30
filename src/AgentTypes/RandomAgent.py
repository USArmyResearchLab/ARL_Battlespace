# -*- coding: utf-8 -*-
"""
@author: berend
"""

from src.AgentModule import AgentClass
from random import sample, random
from collections import defaultdict
import itertools
import src.StateModule

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

class UniformRandomAgentClass(AgentClass):
    def __init__(self, ID):
        AgentClass.__init__(self, ID)
        self.PrintOn = False

    def chooseActions(self, ObservedState, State):
        Actions = []
        for UnitID, Units in ObservedState.items():
            if len(Units)== 1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0)
                # Generate possible actions for the unit based on BoardSize and Position
                ActionOptions = Unit.possibleActions(State)
                #print(ActionOptions,"\n")
                TakenAction = (Unit.ID, [ sample(Options,1)[0] for Options in ActionOptions ])
                Actions.append(TakenAction)
                if self.PrintOn:
                    print("Agent ID=",self.ID, " takes action ", TakenAction[1]," with Unit ID=", UnitID, " of type ", type(Unit),".\n")
        return Actions

    def updateDecisionModel(self, Observations, PriorActions):
        pass


class StaticRandomAgentClass(AgentClass):
    def __init__(self, ID, ActionWeights=None):
        AgentClass.__init__(self, ID)
        self.ActionWeights = ActionWeights

    def chooseActions(self, ObservedState, State):
        """
        TODO: include `State` dependence and reweighting depending on rule restrictions.
        """
        Actions = []
        for UnitID, Units in ObservedState.items():
            # Only for units identified as this agent's will actions be chosen.
            if len(Units) == 1 and nth(Units, 0).Owner == self.ID:
                Unit = nth(Units, 0)
                UnitType = type(Unit)
                UnitActions = []
                # Cycle through each simultaneous possible action select an option dictated by its associated probability.
                for ActionOptions, LocalWeights in zip(Unit.possibleActions(State), self.ActionWeights[UnitType]):
                    RandomNumber = random()*sum( [ LocalWeights[Action] for Action in ActionOptions ] )
                    for Action in ActionOptions:
                        TakenAction = Action
                        RandomNumber -= LocalWeights[Action]
                        if RandomNumber <= 0:
                            break
                    UnitActions.append(TakenAction)
                Actions.append((Unit.ID, UnitActions))
        return Actions

    def updateDecisionModel(self, Observations, PriorActions):
        pass

class DynamicRandomAgentClass(AgentClass):
    """
    Baseline random agent that chooses has dynamic weights instead of static action weights
    
    Note: This class is currently the same as the `StaticRandomAgentClass`
    
    This is a subclass of the AgentClass

    Virtual Functions
    -----------------
    - `chooseActions` selects actions
    - `updateDecisionModel` updates the set of action weights (currently not implemented)

    Attributes
    ----------
    ID:
        a unique identifier of this unit
    ActionWeights:
        a dict of action weights for each unit type when the unit is in state 1
    ActionWeights2:
        a dict of action weights for each unit type when the unit is in state 2

    """
    def __init__(self, ID, ActionWeights=None, ActionWeights2 = None):
        AgentClass.__init__(self, ID)
        self.ActionWeights = ActionWeights
        self.ActionWeights2 = ActionWeights2

    def chooseActions(self, ObservedState, State):
        """
        TODO: include `State` dependence and reweighting depending on rule restrictions.
        """
        Actions = []
        for UnitID, Units in ObservedState.items():
            # Only for units identified as this agent's will actions be chosen.
            if len(Units) == 1 and nth(Units, 0).Owner == self.ID:
                Unit = nth(Units, 0)
                UnitType = type(Unit)
                UnitActions = []
                # Cycle through each simultaneous possible action select an option dictated by its associated probability.
                for ActionOptions, LocalWeights in zip(Unit.possibleActions(State), self.ActionWeights[UnitType]):
                    RandomNumber = random()*sum( [ LocalWeights[Action] for Action in ActionOptions ] )
                    for Action in ActionOptions:
                        TakenAction = Action
                        RandomNumber -= LocalWeights[Action]
                        if RandomNumber <= 0:
                            break
                    UnitActions.append(TakenAction)
                Actions.append((Unit.ID, UnitActions))
        return Actions

    def updateDecisionModel(self, Observations, PriorActions):
        pass
