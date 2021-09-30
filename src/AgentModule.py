#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 21:50:56 2020

@author: berend
"""

class AgentClass(object):
    """
    Abstract class for agents.
    
    Mandatory Virtual Functions
    -----------------
    - `chooseActions` selects actions
    - `updateDecisionModel` updates the set of action weights 

    Attributes
    ----------
    ID:
        a unique identifier of this unit

    """

    def __init__(self,ID):
        self.ID = ID

    def chooseActions(self, ObservedState, State):
        raise NotImplementedError(str(self.__class__.__name__) + " <: AgentClass is an abstract class that requires `chooseActions` to be defined by derived specific classes")
    def updateDecisionModel(self, Observations, PriorActions):
        raise NotImplementedError(str(self.__class__.__name__) + " <: AgentClass is an abstract class that requires `updateDecisionModel` to be defined by derived specific classes")

