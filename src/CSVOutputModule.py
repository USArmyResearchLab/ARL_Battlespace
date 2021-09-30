# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 14:14:29 2021

@author: james.z.hare
"""

import re
import csv
from copy import deepcopy

def getAgentObservations(GameHistory, GameDic, FileName):
    '''
    Creates a list of the observed state of each unit for each agent and turn
    
    Print the observed state to a csv file
    
    Note that the headings depend on the unit with the maximum number of visible cells and actions 
    '''
    
    # OutputList is the full set of observations and headings
    OutputList = [ [ 'Turn', 'AgentID', 'TeamID', 'UnitID', 'UnitType', 'VisibleRange', 'Health', 'Position', 'Orientation', ] ]
    ObservationHistory = GameHistory['AgentObservationLogs']
    ActionHistory = GameHistory['AgentActions']
    State = GameHistory['StateLog']
    GameResult = GameHistory['GameResult']
    if 'Mutual' in GameResult:
        WinningTeam = None
    else:
        WinningTeam = int(re.search(r'\d+', GameResult).group())
    
    # Find Max Number of Actions and Max Number of cells
    MaxActions = 0
    MaxVisibleCells = 0
    AgentTeamIDs = {}
    for AgentID in ObservationHistory.keys():
        TeamID = GameDic[AgentID].TeamID
        AgentTeamIDs[AgentID] = TeamID
        if len(ObservationHistory[AgentID])>0:
            TempObservationHistory = deepcopy(ObservationHistory[AgentID][0])
            for UnitSet in TempObservationHistory.values():
                Unit = UnitSet.pop()
                NumActions = len(Unit.ActionOptions[0])
                if NumActions>MaxActions:
                    MaxActions = NumActions
                NumCells = (Unit.VisibleRange*2 + 1)**3
                if NumCells > MaxVisibleCells:
                    MaxVisibleCells = NumCells
                    
    
    # Update Headings to include the number of visible cells and action number
    for Cell in range(MaxVisibleCells):
        OutputList[0].append(f'Cell {Cell}')
    for ActionNumber in range(MaxActions):
        OutputList[0].append(f'Action {ActionNumber}')
    OutputList[0].append('Win')
    
    # Find the original unit ids and team ids
    OriginalUnits = State[0].Units.keys()  
    
    # Cycle through agents
    for AgentID in ObservationHistory.keys():
        NumTurns = len(ObservationHistory[AgentID])
        TeamID = GameDic[AgentID].TeamID
        # Cycle through turns
        for Turn in range(NumTurns):
            for UnitID, Unit in State[Turn].Units.items():
                TempOutput = [ Turn, AgentID, TeamID, ]
                if Unit.Owner == AgentID and UnitID in OriginalUnits:
                    Position = Unit.Position
                    TempOutput.append(UnitID)
                    TempOutput.append(type(Unit))
                    TempOutput.append(Unit.VisibleRange)
                    TempOutput.append(Unit.Health)
                    TempView = [ None for i in range(MaxVisibleCells) ]
                    TempAction = [ None for i in range(MaxActions) ]
                    if Unit.Health == 0:
                        TempOutput.append(None) # Position = None
                        TempOutput.append(None) # Orientation = None
                        for i in range(MaxVisibleCells):
                            TempOutput.append(TempView[i])
                        for i in range(MaxActions):
                            TempOutput.append(TempAction[i])
                    else:
                        TempOutput.append(Unit.Position)
                        TempOutput.append(Unit.Orientation)
                        # Cycle through other observed units to identify if any are located in the units visible range
                        TempView = [ None for i in range(MaxVisibleCells) ] # TempView cycles through x then y then z
                        for OtherUnitID in ObservationHistory[AgentID][Turn].keys():
                            if len(ObservationHistory[AgentID][Turn][OtherUnitID])==0:
                                continue
                            OtherUnitSet = iter(ObservationHistory[AgentID][Turn][OtherUnitID])
                            OtherUnit = next(OtherUnitSet)
                            OtherPosition = OtherUnit.Position
                            Index = 0
                            # Cycle through the visible cells and 
                            for ZVal in range(int(Position[2])-Unit.VisibleRange, int(Position[2])+Unit.VisibleRange+1):
                                for YVal in range(int(Position[1])-Unit.VisibleRange, int(Position[1])+Unit.VisibleRange+1):
                                    for XVal in range(int(Position[0])-Unit.VisibleRange, int(Position[0])+Unit.VisibleRange+1):
                                        # Check if other unit is located in the cell
                                        if OtherPosition == (XVal, YVal, ZVal):
                                            if OtherUnit.Owner == None:
                                                TempView[Index] = f'[Enemy, {type(OtherUnit)}]'
                                            elif OtherUnit.ID != Unit.ID:
                                                TempView[Index] = f'[Friendly, {type(OtherUnit)}]'
                                        if Position == (XVal, YVal, ZVal):
                                            TempView[Index] = 'Self'
                                        Index += 1
                        # Update TempOutput
                        for i in range(MaxVisibleCells):
                            TempOutput.append(TempView[i])
                        # Identify which action was taken
                        TempAction = [ None for i in range(MaxActions) ]
                        Index = 0
                        for Action in Unit.ActionOptions[0]:
                            for ActionIndx in range(len(ActionHistory[AgentID][Turn])):
                                Pair = ActionHistory[AgentID][Turn][ActionIndx]
                                if Pair[0] == Unit.ID and Pair[1][0] == Action:
                                    TempAction[Index] = 1
                            Index += 1
                        # Update TempOutput
                        for i in range(MaxActions):
                            TempOutput.append(TempAction[i])
                    
                    # Add Winner
                    if TeamID == WinningTeam:
                        TempOutput.append(1)
                    else:
                        TempOutput.append(0)
                        
                    # Update observed state
                    OutputList.append(TempOutput)
            
    # Write to CSV file
    Headings = OutputList[0]
    Data = OutputList[1:]
    with open(FileName, 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(Headings) 
        csvwriter.writerows(Data)
    
    return OutputList
