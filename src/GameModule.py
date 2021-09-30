#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:13:28 2020

@author: berend
"""

from copy import deepcopy
from collections import defaultdict, Set
from src.StateModule import StateClass

class GameClass(object):
    """
        Class to define a specific game between agents.

        Virtual Methods
        ---------------
        Any specialization of this class requires:
        - `resolveActions(StateChanges)` to update the game state given the rules for legal actions, where `StateChanges` is a list of tuples `(UnitID, Unit)` indicating which `UnitID` is being replaced with `Unit`.
        - `continueGame(State)` determines whether the game state `State` indicates the end of the game.

        Methods
        -------
        `observe(State: StateClass)`
            generates the observations for each agent.
    """
    def __init__(self, Agents):
        " Constructor from `Agents: dict{ID:Agent}`"
        if not isinstance(Agents, dict):
            raise TypeError("Agents not a dict ")
        KeyPairs = [ (key, Agent.ID) for (key, Agent) in Agents.items() ]
        if any([ key != ID for (key, ID) in KeyPairs]):
            raise RuntimeError(" Inconsistent IDs in "+str(KeyPairs))
        self.Agents = deepcopy(Agents)
        self.PrintOn = False

    def play(self, State: StateClass):
        """
            Play a game starting from `State`
        """
        AgentObservationLogs = { AgentID: [] for AgentID in self.Agents.keys() }
        AgentActions = { AgentID: [] for AgentID in self.Agents.keys()}
        StateLog = [State]
        GameOn = True
        Turns = 1
        while GameOn:
            if self.PrintOn:
                print('------------------------------New Turn '+str(Turns)+' -------------------------------\n')
            Turns += 1
            NewState = deepcopy(State)
            Changes = []
            ObservedStates = self.observe(NewState)
            for (AgentID, ObservedState) in ObservedStates.items():
                Agent = self.Agents[AgentID]
                AgentObservationLogs[AgentID].append(ObservedState)
                Agent.updateDecisionModel(AgentObservationLogs[Agent.ID], AgentActions[Agent.ID])
                AgentAction = Agent.chooseActions(ObservedState, State)
                for (UnitID, Actions) in AgentAction:
                    Changes.extend(State.Units[UnitID].execute(Actions, State))
                AgentActions[Agent.ID].append(AgentAction)
            self.resolveActions(NewState,Changes)
            StateLog.append(NewState)
            State = NewState
            GameOn = self.continueGame(State)
        return State, StateLog, AgentActions, AgentObservationLogs

    def observe(self, State):
        """
        Identify what agents can determine of `State`

        Parameters
        ----------
        State : StateClass
            Ground truth which is observed.

        Returns
        -------
        ObservedStates : dict(dict(set))
            Dictionary collecting observations each agent with `AgentID` has made of state `State` via its units.

        """
        ObservedStates = defaultdict(lambda: defaultdict(set))
        for Observer in State.Units.values():
            AgentID = Observer.Owner
            for (UnitID, Unit) in State.Units.items():
                NewUnit = Observer.observe(Unit)
                if NewUnit is not None:
                    NewUnit = self.correctObservation(Observer, Unit, NewUnit)
                    ObservedStates[AgentID][UnitID].add(NewUnit)
        if len(ObservedStates.keys()) == 0:
            if self.PrintOn:
                print(State)
        return ObservedStates

    def correctObservation(self, Observer, Unit, ObservedUnit):
        # do something in a specific game
        return ObservedUnit
