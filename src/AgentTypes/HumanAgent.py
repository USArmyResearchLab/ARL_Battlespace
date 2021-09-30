# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:13:21 2020

@author: james.z.hare
"""

from src.AgentModule import AgentClass
import itertools

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

def getUnitAction(UnitID, ActionOptions, msg):
    """
    Prompts the Human agent to select an action for the Unit. 
    If only one action is available, that action will be automatically selected
    
    Parameters
    ----------
    UnitID: [int] 
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
    msg += f"Which of the following action would you like to take for Unit ID = {UnitID}?"
    print("Which of the following action would you like to take for Unit ID = %s?" %(UnitID))
    for ActionCount in range(len(ActionOptions[0])):
        msg += f"{ActionCount} - {ActionOptions[0][ActionCount]}\n"
        print(ActionCount, " - ",ActionOptions[0][ActionCount])
    
    BadInput = True
    while BadInput:
        UserInput = input(":")
        if int(UserInput) in range(len(ActionOptions[0])):
            ActionCount = int(UserInput)
            Action = ActionOptions[0][ActionCount]
            break
        else:
            print("Invalid input, please try again.")
    return Action

class HumanAgentClass(AgentClass):
    def __init__(self, ID):
        AgentClass.__init__(self, ID)

    def chooseActions(self, ObservedState, State):
        """
        Print the observed state of the human agent and prompt them to select a legal action for each unit
    
        Parameters
        ----------
        ObservedState: [dict] 
            A dictionary of the Units seen by the human agent
        State: StateClass

        Returns
        -------
        Actions: list[str]
            The actions selected by the Human agent
        """
        msg = self.printObservedState(ObservedState)
        Actions = []
        for UnitID, Units in ObservedState.items():
            if len(Units)== 1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0)
                # Generate possible actions for the unit based on BoardSize and Position
                ActionOptions = Unit.possibleActions(State)
                TakenAction = (Unit.ID, [ getUnitAction(UnitID, ActionOptions, msg) ])
                Actions.append(TakenAction)
                print("Agent ID=",self.ID, " takes action ", TakenAction[1]," with Unit ID=", UnitID, ".\n")
        return Actions
    
    def getActions(self, ObservedState, State):
        for UnitID, Units in ObservedState.items():
            if len(Units)==1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0)
                ActionOptions = Unit.possibleActions(State)
        return ActionOptions

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
            msg += f"|     {nth(Units,0).Owner}    |    {UnitID}    | {nth(Units,0).Position}|  {nth(Units,0).Orientation} | {type(nth(Units,0))} |\n"
        msg += "------------------------------------------------------------------------\n"
        
        print(msg)
        return msg
        
#        print("Agent %s's Turn \n\nObserved State for Agent %s on Team %s:\n" %(self.ID, self.ID, self.TeamID))
#        print("------------------------------------------------------------------------")
#        print("| Agent ID | Unit ID | Position | Orientation |         Class          |")
#        print("------------------------------------------------------------------------")
#        
#        for UnitID, Units in ObservedState.items():
#            print("|     %s    |    %s    | %s|  %s | %s |" %(nth(Units,0).Owner, UnitID, nth(Units,0).Position, nth(Units,0).Orientation, type(nth(Units,0))))
#        print("------------------------------------------------------------------------\n")
    
    def updateDecisionModel(self, Observations, PriorActions):
        pass
