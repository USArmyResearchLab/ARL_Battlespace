# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 15:38:38 2020

@author: james.z.hare
"""

from src.AgentTypes.HumanAgent import HumanAgentClass
from src.AgentTypes.RandomAgent import UniformRandomAgentClass, StaticRandomAgentClass, DynamicRandomAgentClass
import itertools
import numpy as np
from copy import deepcopy
from src.UnitTypes.ProjectileModule import ProjectileClass
from src.UnitTypes.ExampleUnit import FlagClass
from src.UnitTypes.SoldierModule import SoldierClass
from src.UnitTypes.TankModule import TankClass
from src.UnitTypes.TruckModule import TruckClass
from src.UnitTypes.AirplaneModule import AirplaneClass
import math
from random import sample, random, randint

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

def getUnitAction(UnitType, ActionOptions, msg, ActionNames):
    """
    Prompts the Human agent to select an action for the Unit. 
    If only one action is available, that action will be automatically selected
    
    Parameters
    ----------
    Unit: [UnitClass] 
        ID of Unit to be altered
    ActionOptions: [list]
        Set of actions available for the unit

    Returns
    -------
    Action: [str]
        The action selected by the Human agent
    """
    # If only one action is available, return it and do not prompt user
    if len(ActionOptions[0])==1:
        return ActionOptions[0][0]
    
    # If multiple actions are available, prompt the user
    msg += f"Which of the following actions would you like to take for Unit {UnitType}?"
    print("Which of the following actions would you like to take for Unit %s?" %(UnitType))
    for ActionCount in range(len(ActionOptions[0])):
        msg += f"{ActionCount} - {ActionNames[0][ActionCount]}\n"
        print(ActionCount, " - ",ActionNames[0][ActionCount])
        #print(ActionCount, " - ",ActionOptions[0][ActionCount])
        
    BadInput = True
    while BadInput:
        try:
            UserInput = int(input(":"))
            if UserInput in range(len(ActionOptions[0])):
                ActionCount = UserInput
                Action = ActionOptions[0][ActionCount]
                break
            else:
                print("Invalid input, please try again.")
        except ValueError:
            print("Invalid input, please try again.")
    return Action

class TeamHumanAgentClass(HumanAgentClass):
    def __init__(self, ID, TeamID):
        HumanAgentClass.__init__(self, ID)
        self.TeamID = TeamID
    
    def printObservedState(self, ObservedState):
        """
        Print the observed state of the human agent
    
        Parameters
        ----------
        ObservedState: [dict] 
            A dictionary of the Units seen by the human agent

        Returns
        -------
        None
        """
        msg = f"Agent {self.ID}'s Turn \n\nObserved State for Agent {self.ID} on Team {self.TeamID}:\n"
        msg += "------------------------------------------------------------------------\n"
        msg += "| Agent ID | Unit ID | Position | Orientation |         Class          |\n"
        msg += "------------------------------------------------------------------------\n"
        for UnitID, Units in ObservedState.items():
            Position = None
            if nth(Units,0).Position != None:
                Position = tuple(int(nth(Units,0).Position[Cor]) for Cor in range(3))
            if nth(Units,0).Orientation != None:
                Orientation = tuple(int(nth(Units,0).Orientation[Cor]) for Cor in range(3))
            msg += f"|     {nth(Units,0).Owner}    |    {UnitID}    | {Position}|  {Orientation} | {type(nth(Units,0))} |\n"
        msg += "------------------------------------------------------------------------\n"
        
        #print(msg)
        return msg
    
    def getActions(self, ObservedState, State):
        msg = self.printObservedState(ObservedState)
        ActionOptions = {}
        for UnitID, Units in ObservedState.items():
            if len(Units)==1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0)
                ActionOptions[UnitID] = Unit.possibleActions(State)
        return {0: ActionOptions, 1: msg}
    
    def updateDecisionModel(self, Observations, PriorActions):
        pass
    
class TeamUniformRandomAgentClass(UniformRandomAgentClass):
    def __init__(self, ID, TeamID):
        UniformRandomAgentClass.__init__(self, ID)
        self.TeamID = TeamID
        self.Went = 0
       
class TeamStaticRandomAgentClass(StaticRandomAgentClass):
    def __init__(self, ID, TeamID, ActionWeights, ProbabilityMap):
        StaticRandomAgentClass.__init__(self, ID, ActionWeights)
        self.TeamID = TeamID
        self.Went = 0
        self.ProbabilityMap = ProbabilityMap
        self.OpponentFlagLocations = None
        self.DefaultWeights = deepcopy(ActionWeights)
        
    def updateDecisionModel(self, Observations, PriorActions):
        pass

class TeamDecisionTreeRandomAgentClass(DynamicRandomAgentClass):
    """
    The agent implemented in the SPIE paper. This agent identifies the state of the unit
    and chooses the actions based on the state. 
    
    Note: The use of joint probabilities between two units needs to be updated, but
    setting the TreeDepth = 1 implements the actionWeights for individual Units
    
    This is a subclass of the DynamicRandomAgentClass

    Virtual Functions
    -----------------
    - `chooseActions` selects actions
    - `updateDecisionModel` updates the set of action weights
    - `getUnitStates` gets the state of each unit the agent owns. The definition of states are those used in the SPIE paper. 

    Attributes
    ----------
    ID:
        a unique identifier of this agent
    TeamID:
        a unique identifier of the agents team
    SingleUnitActionWeights:
        a dict of action weights for each unit type generated from two Human game play data
    UnitPairsActionWeights:
        a dict of action weights for joint actions for pairs of units generated from two Human game play data
    DefaultWeights:
        a dict of default action weights
    TreeDepth:
        1 indicates single unit decision model, while 2 indicates joint unit decision model
        Note that in the current state of this class, a TreeDepth = 2 does not work properly and can only 
        be used with the game set up where we had 2 humans playing 2 random agents
    OpponentFlagLocations:
        the location of the opponents flags
    FlagSeen:
        an indicator variable of whether a flag has been seen by the agent
    ControlledUnits:
        set of units that are controllable

    """    
    
    def __init__(self, ID, TeamID, SingleUnitActionWeights, UnitPairsActionWeights, DefaultWeights, TreeDepth = 1):
        DynamicRandomAgentClass.__init__(self, ID)
        self.TeamID = TeamID
        self.OpponentFlagLocations = None
        self.SingleUnitActionWeights = SingleUnitActionWeights
        self.UnitPairsActionWeights = UnitPairsActionWeights
        self.DefaultWeights = DefaultWeights
        self.FlagSeen = 0
        self.TreeDepth = TreeDepth
        self.ControlledUnits = {SoldierClass, TankClass, TruckClass, AirplaneClass}

    def chooseActions(self, ObservedState, State):
        """
        TODO: Update TreeDepth = 2 code to implement joint action pairs
        """
        
        Actions = []
        if self.TreeDepth == 2: # Joint action probabilities will be used
            # Identify the agents ground units that are alive
            AliveGroundUnits = {}
            for UnitID, Units in ObservedState.items():
                if len(Units)==1 and nth(Units,0).Owner == self.ID:
                    Unit = nth(Units,0)
                    UnitType = type(Unit)
                    if UnitType != AirplaneClass and any([isinstance(Unit,T) for T in self.ControlledUnits]):
                        AliveGroundUnits[UnitID] = nth(Units,0)
            
            # Play the tournament with the alive units
            AliveIDs = list(AliveGroundUnits.keys())
            if len(AliveIDs)>0:
                # Select the alive unit to choose their decision first
                FirstUnitID = AliveIDs[randint(0,len(AliveIDs)-1)] 
                FirstUnit = AliveGroundUnits[FirstUnitID]
                FirstUnitType = type(FirstUnit)
                
                UnitIndex = []
                TempActions = []
                UnitActions = []
                OtherUnitIDs = []
                for Pair in self.ActionWeights[FirstUnitType]:
                    # Identify the unit pair and the index of the first selected unit
                    UnitPair = list(Pair.keys())
                    ActionPair = list(Pair.values())
                    OtherUnitID = UnitPair[0][0]
                    if FirstUnitID == OtherUnitID: # Then other unit id is in the second element
                        OtherUnitID = UnitPair[0][1]
                        UnitIndex.append(0)
                    else:
                        UnitIndex.append(1)
                    OtherUnitIDs.append(OtherUnitID)
                    # Get the possible actions for both units
                    PossibleActions1 = FirstUnit.possibleActions(State)
                    if OtherUnitID not in ObservedState.keys(): # Other Unit is dead (Need to updated based on health)
                        PossibleActions2 = (('doNothing',),)
                    else:
                        Unit2 = nth(ObservedState[OtherUnitID], 0)
                        PossibleActions2 = Unit2.possibleActions(State)
                    # Identify the set of possible action pairs of the two units
                    # Must check the pair order 
                    ActionList = ()
                    if UnitIndex[-1] == 0:
                        for Action1 in PossibleActions1[0]:
                            for Action2 in PossibleActions2[0]:
                                ActionList += ((Action1,Action2),)
                    else:
                        for Action2 in PossibleActions2[0]:
                            for Action1 in PossibleActions1[0]:
                                ActionList += ((Action2,Action1),)
                    # Select the action
                    for ActionOptions, LocalWeights in zip((ActionList,), tuple(ActionPair)):
                        RandomNumber = random()*sum( [ LocalWeights[Action] for Action in ActionOptions ] )
                        for Action in ActionOptions:
                            TakenAction = Action
                            RandomNumber -= LocalWeights[Action]
                            if RandomNumber <= 0:
                                break
                        TempActions.append(TakenAction)
                # Select one of the action pairs at random
                if random()<=0.5:
                    UnitActions.append(TempActions[0][UnitIndex[0]]) # First Unit action
                    UnitActions.append(TempActions[0][UnitIndex[1]]) # Second Unit action
                    OtherUnitIndex = 0
                else:
                    UnitActions.append(TempActions[1][UnitIndex[1]])
                    UnitActions.append(TempActions[1][UnitIndex[0]])
                    OtherUnitIndex = 1
                FirstUnitAction = UnitActions[0]
                SecondUnitAction = UnitActions[1]
                
                Actions.append((FirstUnitID, FirstUnitAction))
                Actions.append((OtherUnitIDs[OtherUnitIndex], SecondUnitAction))
                
                # Loop through all alive ground units 
                # Idnetify the other pair and update the remaining units action
                # This needs to be updated
                for UnitID, Unit in AliveGroundUnits.items():
                    if UnitID != FirstUnitID:
                        UnitActions = []
                        for Pair in self.ActionWeights[type(Unit)]:
                            
                            UnitPair = list(Pair.keys())
                            ActionPair = list(Pair.values())
                            if FirstUnitID not in UnitPair[0]:
                                UnitIndex = UnitPair[0].index(UnitID)
                                FirstUnitIndex = UnitPair[0].index(FirstUnitID)
                                PossibleActions = Unit.possibleActions(State)
                                MarginalActionWeights = {}
                                for Action, ActionWeight in ActionPair[0].items():
                                    if Action[FirstUnitIndex] == FirstUnitAction[0]:
                                        MarginalActionWeights[Action[UnitIndex]] = ActionWeight
                                TotalSum = sum(list(MarginalActionWeights.values()))
                                MarginalWeights = {Action: ActionWeight/TotalSum for Action, ActionWeight in MarginalActionWeights.items()}
                                for ActionOptions, LocalWeights in zip(PossibleActions, ((MarginalWeights),)):
                                    RandomNumber = random()*sum( [ LocalWeights[Action] for Action in ActionOptions ] )
                                    for Action in ActionOptions:
                                        TakenAction = Action
                                        RandomNumber -= LocalWeights[Action]
                                        if RandomNumber <= 0:
                                            break
                                    UnitActions.append(TakenAction)
                        Actions.append((UnitID, UnitActions))

        # Select the action for each unit using the single unit probabilities
        for UnitID, Units in ObservedState.items():
            if len(Units) == 1 and nth(Units, 0).Owner == self.ID and any([UnitID in TakenActions for TakenActions in Actions])==False:
                Unit = nth(Units, 0)
                UnitType = type(Unit)
                UnitActions = []
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
        """
        TODO: Update TreeDepth = 2 code to implement joint action pairs
        """
        Weights = self.DefaultWeights
        self.ActionWeights = deepcopy(Weights)
        AgentsUnits = {}
        TeamMatesUnits = {}
        EnemyUnits = {}
        Observed = deepcopy(Observations[0])
        for UnitID, SetOfUnits in Observed.items():
            Unit = SetOfUnits.pop()
            if Unit.ID == None:
                EnemyUnits[UnitID] = Unit
            elif Unit.Owner == self.ID:
                AgentsUnits[UnitID] = Unit
            else:
                TeamMatesUnits[UnitID] = Unit
        UnitStates = self.getUnitStates(AgentsUnits,TeamMatesUnits,EnemyUnits)
        
        if self.TreeDepth == 1:
            for UnitID, Unit in AgentsUnits.items():
                if any([isinstance(Unit,T) for T in self.ControlledUnits]):
                    State = UnitStates[UnitID]
                    UnitWeights = self.SingleUnitActionWeights[State][type(Unit)]
                    if math.isnan(sum(UnitWeights[0].values()))==False:
                        self.ActionWeights[type(Unit)] = deepcopy(UnitWeights)
        else:
            # Needs to be updated
            for UnitID, Unit in AgentsUnits.items():
                if isinstance(Unit,AirplaneClass):
                    State = UnitStates[UnitID]
                    UnitWeights = self.SingleUnitActionWeights[State][type(Unit)]
                    if math.isnan(sum(UnitWeights[0].values()))==False:
                        self.ActionWeights[type(Unit)] = deepcopy(UnitWeights)
                elif any([isinstance(Unit,T) for T in self.ControlledUnits]):
                    self.ActionWeights[type(Unit)] = ()
                    State = UnitStates[UnitID]
                    for UnitPairs in self.UnitPairsActionWeights.keys():
                        if UnitID in UnitPairs:
                            UnitID2 = UnitPairs[0]
                            if UnitID2 == UnitID:
                                UnitID2 = UnitPairs[1]
                            State2 = 8
                            if UnitID2 in UnitStates.keys():
                                State2 = UnitStates[UnitID2]
                            UnitWeights = self.UnitPairsActionWeights[UnitPairs][(State,State2)][type(Unit)]
                            self.ActionWeights[type(Unit)] += ({UnitPairs: deepcopy(UnitWeights[0])},)
                            
        
        
    def getUnitStates(self, AgentsUnits, TeamMatesUnits, EnemyUnits):
        
        # Check for friendlys
        UnitStates = {}
        for UnitID, Unit in AgentsUnits.items():
            if any([isinstance(Unit,T) for T in self.ControlledUnits]):
                UnitStates[UnitID] = [1, 1, 1, 0, 0, 0]
                Position = Unit.Position
                for TeamUnitID, TeamUnit in TeamMatesUnits.items():
                    if isinstance(TeamUnit,FlagClass) == False:
                        TeamPosition = TeamUnit.Position
                        Distance = ( (Position[0]-TeamPosition[0])**2 + (Position[1]-TeamPosition[1])**2 )**0.5
                        if Position[2] == 0 and TeamPosition[2] == 0: #Ground Units
                            if Distance <= ( 2*Unit.VisibleRange )**0.5:
                                UnitStates[UnitID][0] = 0
                                UnitStates[UnitID][3] = 1
                        elif Position[2] == 1: # AirUnits
                            if Distance <= ( 2*Unit.VisibleRange )**0.5:
                                UnitStates[UnitID][0] = 0
                                UnitStates[UnitID][3] = 1
                for EnemyUnitID, EnemyUnit in EnemyUnits.items():
                    EnemyPosition = EnemyUnit.Position
                    Distance = ( (Position[0]-EnemyPosition[0])**2 + (Position[1]-EnemyPosition[1])**2 )**0.5
                    if isinstance(EnemyUnit,FlagClass):
                        if Distance <= ( 2*Unit.VisibleRange )**0.5:
                            UnitStates[UnitID][2] = 0
                            UnitStates[UnitID][5] = 1
                            self.FlagSeen = 1
                    else:
                        if Position[2] == 0 and EnemyPosition[2] == 0 and Distance <= (2*Unit.VisibleRange)**0.5:
                            UnitStates[UnitID][1] = 0
                            UnitStates[UnitID][4] = 1
        # have to loop through again to updated based on flagseen
        StateID = {}
        for UnitID, UnitState in UnitStates.items():
            if self.FlagSeen == 1:
                UnitState[2] = 0
                UnitState[5] = 1
            
            if UnitState[0]==1 and UnitState[1]==1 and UnitState[2]==1:
                StateID[UnitID] = 0
                # State 0 is No Friendly, No Enemy, No Flag
            if UnitState[0]==1 and UnitState[1]==1 and UnitState[5]==1:
                StateID[UnitID] = 1
                # State 1 is No Friendly, No Enemy, Flag Seen
            if UnitState[0]==1 and UnitState[4]==1 and UnitState[2]==1:
                StateID[UnitID] = 2
                # State 2 is No Friendly, Enemy Present, No Flag
            if UnitState[3]==1 and UnitState[1]==1 and UnitState[2]==1:
                StateID[UnitID] = 3
                # State 3 is Friendly Present, No Enemy, No Flag
            if UnitState[3]==1 and UnitState[4]==1 and UnitState[2]==1:
                StateID[UnitID] = 4
                # State 4 is Friendly Present, Enemy Present, No Flag
            if UnitState[3]==1 and UnitState[1]==1 and UnitState[5]==1:
                StateID[UnitID]= 5
                # State 5 is Friendly Present, No Enemy, Flag Seen
            if UnitState[0]==1 and UnitState[4]==1 and UnitState[5]==1:
                StateID[UnitID] = 6
                # State 6 is No Friendly, Enemy Present, Flag Present
            if UnitState[3]==1 and UnitState[4]==1 and UnitState[5]==1:
                StateID[UnitID] = 7
                # State 7 is Friendly Present, Enemy Present, Flag Present
        
        return StateID
        
