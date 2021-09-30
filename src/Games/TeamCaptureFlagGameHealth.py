# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 12:23:27 2020

@author: james.z.hare
"""

from copy import deepcopy
from src.GameModule import GameClass
# from StateModule import StateClass
from collections import defaultdict, Set
from src.StateTypes.TeamState import TeamStateClass
from src.UnitTypes.ProjectileModule import ProjectileClass
from src.UnitTypes.ExampleUnit import ExampleUnit
from src.UnitTypes.ExampleUnit import FlagClass
from src.UnitTypes.SoldierModule import SoldierClass
from src.UnitTypes.TankModule import TankClass
from src.UnitTypes.TruckModule import TruckClass
from src.UnitTypes.AirplaneModule import AirplaneClass
from src.AgentTypes.RemoteAgent import RemoteTeamAgentClass
import dill as pickle
from reliableSockets import sendReliablyBinary


def first(D):
    for key in D.keys():
       return D[key]
    return None

class TeamCaptureFlagClass(GameClass):
    """
    Class to define a Capture the Flag game between teams of agents.
    Here, each agent owns a flag and the game concludes when all `FlagCapture` units are elimiated or all flags are captured from a team

        Methods
        -------
        `resolveActions(State: TeamStateClass)`
            Updates the state based on the actions taken by each agent
        `continueGame(State: TeamStateClass)`
            Defines whether the game should continue or not
        `observe(State: TeamStateClass)`
            generates the observations for each agent, which includes their teammates observations
        `play(State: TeamStateClass)`
            plays the game and returns the full state of the game
        `correctObservation(Observer, Unit, ObservedUnit)`
            resolves the information observed by each agent
    """

    def __init__(self, Agents):
        GameClass.__init__(self, Agents)
        self.FlagCapturers = ( ExampleUnit, SoldierClass, TankClass, TruckClass, )
        self.ObservableUnits = ( SoldierClass, TankClass, TruckClass, AirplaneClass, FlagClass )
        self.FiniteLifeUnits = ( ProjectileClass, ) # Implemented such that a projectile can only travel a fixed number of cells
        self.BypassUnits = ( ) # Implemented such that certain UnitClass's cannot collide with eachother
        self.Changes = []
        self.PlayersPlayed = 0
        self.GameOn = 0
        self.NumberOfPlayers = len(Agents.keys())

    def resolveActions(self, State: TeamStateClass, Changes):
        """
        Resolve contradictory actions and update the state.

        Parameters
        ----------
        State : TeamStateClass
            State on which to resolve the actions.
        Changes : list
            List of tuples `(UnitID, Unit: UnitClass)`.

        Returns
        -------
        State.

        """
        ValidChanges = [x for x in Changes if x is not None]
        UnitChanges = defaultdict(set)
        msg = "Changes from previous turn: \n \n"

        PreviousState = deepcopy(State)
        
        # Give units with ID = None a new ID
        for (UnitID, NewUnit) in ValidChanges:
            if UnitID is None:
                UnitID = State.newUnitID()
                NewUnit.ID = UnitID
                State.Units[UnitID] = NewUnit
                PreviousNewUnit = deepcopy(NewUnit)
                PreviousState.Units[UnitID] = PreviousNewUnit
                # Include the following commented code if you would like a nascent ProjectileClass Unit 
                # to be able to collide on their first turn. 
#                Position = [x for x in NewUnit.Position]
#                Orientation = [x for x in NewUnit.Orientation]
#                PreviousPosition = []
#                for Pos, Ori in zip(Position, Orientation):
#                    PreviousPosition.append(Pos-Ori)
#                PreviousNewUnit.Position = tuple(PreviousPosition)
                print("Gave Agent ID = ", NewUnit.Owner, " a new unit of type", type(NewUnit)," a new ID =", UnitID, " located at ", NewUnit.Position, " with Orientation ", NewUnit.Orientation, ".\n")
            UnitChanges[UnitID].add(NewUnit)

        # Consolidate the results from the various actions
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) >= 1:
                # If any change leads to a removal of a unit it takes precedence
                # and it is removed from the state
                for Unit1 in UnitChanges[UnitID]:
                    if Unit1 is None:                        
                        msg += f"removed unit {State.Units[UnitID]} with {UnitID} because it was destroyed\n"
                        print("removing unit ",State.Units[UnitID]," with ",UnitID," because it was destroyed\n")
                        if isinstance(State.Units[UnitID],ProjectileClass):
                            State.Units.pop(UnitID)
                        else:
                            State.Units[UnitID].Health = 0 # In this game we keep units with 0 health around
                        UnitChanges.pop(UnitID)
                        break

        # Update all units
        for UnitID in UnitChanges.keys():
            if len(UnitChanges[UnitID]) >= 1:
                Unit = UnitChanges[UnitID].pop()
                print("Agent ID = ", Unit.Owner, " changed Unit ", type(Unit), " with ID =",UnitID," position to ",Unit.Position, " and orientation to ", Unit.Orientation, ".\n")
                State.Units[UnitID] = Unit # Only one version will be used.

        RemoveUnits = set()
        RemoveAgents = set()
        # If a unit goes out of bounds, destroy it
        for UnitID, Unit in State.Units.items():
            if any([ Unit.Position[i] >= State.BoardSize[i] for i in range(3) ]):
                msg += f"removing {type(Unit)} of Agent {Unit.Owner} for being outside board (> {State.BoardSize})\n"
                print(msg)
                RemoveUnits.add(UnitID)
            if any([ Unit.Position[i] <0 for i in range(3) ]):
                msg += f"removing {type(Unit)} of Agent {Unit.Owner} for being outside board (< 0)\n"
                print(msg)
                RemoveUnits.add(UnitID)

        # First, check for colliding objects. These are defined as two Units with 
        # different IDs that swap positions.
        # Colliding Units are not two Units that move into the same position
        for UnitID1, Unit1 in State.Units.items():
            if isinstance(Unit1,FlagClass) == False and Unit1.Health != 0:
                for UnitID2, Unit2 in State.Units.items():
                    if isinstance(Unit2,FlagClass) == False and Unit2.Health != 0 :
                        PreviousUnit1 = PreviousState.Units[UnitID1]
                        PreviousUnit2 = PreviousState.Units[UnitID2]
                        if Unit1 != Unit2 and (Unit1.overlaps(PreviousUnit2) and Unit2.overlaps(PreviousUnit1)):
                            # Check whether both Units are ByPassUnits, i.e., they cannot collide
                            if (any([isinstance(Unit1,T) for T in self.BypassUnits]) == False) and (any([isinstance(Unit2,T) for T in self.BypassUnits]) == False):
                                if Unit1.Attack == State.Units[UnitID2].Attack:
                                    if (UnitID1 not in RemoveUnits) and (UnitID2 not in RemoveUnits):
                                        msg += f"Removing {type(Unit1)} of Agent {Unit1.Owner} and {type(Unit2)} of Agent {Unit2.Owner} for colliding.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID1)
                                    RemoveUnits.add(UnitID2)
                                elif Unit1.Attack == 1 and State.Units[UnitID2].Attack == None: # Unit1 is attacking while Unit2 is not
                                    if UnitID2 not in RemoveUnits:
                                        msg += f"Removing {type(Unit2)} of Agent {Unit2.Owner} since it was attacked while colliding with {type(Unit1)} of Agent {Unit1.Owner}.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID2)
                                else:                                           # Unit2 is attacking while Unit1 is not
                                    if UnitID1 not in RemoveUnits:
                                        msg += f"Removing {type(Unit1)} of Agent {Unit1.Owner} since it was attacked while colliding with {type(Unit2)} of Agent {Unit2.Owner}.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID1)
                                
                                
        # Remove all colliding units
        # This is because we are assuming that the colliding units were destroyed   
        # in the middle of their trajectory, i.e., inbetween cells  
        for UnitID in RemoveUnits:
            if isinstance(State.Units[UnitID],ProjectileClass):
                State.Units.pop(UnitID)
            else:
                State.Units[UnitID].Health = 0
        RemoveUnits = set()
                            
        # If two units overlap, they are destroyed.
        for UnitID1, Unit1 in State.Units.items():
            if isinstance(Unit1,FlagClass) == False and Unit1.Health != 0:
                for UnitID2, Unit2 in State.Units.items():
                    if isinstance(Unit2,FlagClass) == False and Unit2.Health != 0:
                        if Unit1 != Unit2 and Unit1.overlaps(Unit2):
                                if Unit1.Attack == Unit2.Attack: # Both units are either attacking or not
                                    if (UnitID1 not in RemoveUnits) and (UnitID2 not in RemoveUnits):
                                        msg += f"Removing {type(Unit1)} of Agent {Unit1.Owner} and {type(Unit2)} of Agent {Unit2.Owner} for overlapping.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID1)
                                    RemoveUnits.add(UnitID2)
                                elif Unit1.Attack == 1 and Unit2.Attack == None: # Unit1 is attacking while Unit2 is not
                                    if UnitID2 not in RemoveUnits:
                                        msg += f"Removing {type(Unit2)} of Agent {Unit2.Owner} since it was attacked by {type(Unit1)} of Agent {Unit1.Owner}.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID2)
                                else:                                           # Unit2 is attacking while Unit1 is not
                                    if UnitID1 not in RemoveUnits:
                                        msg += f"Removing {type(Unit1)} of Agent {Unit1.Owner} since it was attacked by {type(Unit2)} of Agent {Unit2.Owner}.\n"
                                        print(msg)
                                    RemoveUnits.add(UnitID1)
                                    
        
        # If a Finite Life Unit has a life = 0, remove from the game
        for UnitID, Unit in State.Units.items():
            if any([ isinstance(Unit,T) for T in self.FiniteLifeUnits]):
                if Unit.RemainingLifetime == 0:
                    RemoveUnits.add(UnitID)
                    msg += f"Life of {type(Unit)} of Agent {Unit.Owner} expired, thus removed.\n"
                    print(msg)
        
        # If a FlagCapturer unit overlaps a flag that is not part of their team, 
        # capture the flag and remove all units owned by the flag owner
        for Unit in State.Units.values():
            UnitOwner = Unit.Owner
            UnitTeam = self.Agents[UnitOwner].TeamID
            for FlagOwner in State.FlagPosition.keys():
                FlagTeam = self.Agents[FlagOwner].TeamID
                FlagPosition = State.FlagPosition[FlagOwner]
                if Unit.Position == FlagPosition and any([isinstance(Unit,T) for T in self.FlagCapturers]) and FlagTeam != UnitTeam:
                    msg += f"Agent {UnitOwner} captured Agent {FlagOwner}'s Flag\n"
                    print(msg)
                    #print("Agent %s captured Team %s's Flag\n" %(UnitOwner, FlagTeam))
                    # Remove all units from FlagOwner         
                    for EachUnit in State.Units.values():
                        if EachUnit.Owner == FlagOwner:
                            RemoveUnits.add(EachUnit.ID)
                            RemoveAgents.add(FlagOwner)
                            msg += f"Removing {type(EachUnit)} of Agent {EachUnit.Owner} since their flag was captured.\n"
                            print(msg)
                            #msg += f"Removing Unit {EachUnit.ID} since thier flag was captured.\n"
                            #print("Removing Unit %s since their flag was captured" %(EachUnit.ID) )
                    
        # Now remove relevant units
        for UnitID in RemoveUnits:
            if isinstance(State.Units[UnitID],ProjectileClass):
                State.Units.pop(UnitID)
            else:
                State.Units[UnitID].Health = 0
            
        # Report changes to clients
        msg += "New turn starting. Please wait for your turn...\n"
        for Agent in self.Agents.values():
            print(type(Agent))
            if isinstance(Agent, RemoteTeamAgentClass):
                print('sending a pickled message from TeamCaptureFlagGameHealth.py line 244')
                Agent.Connection.send(pickle.dumps(msg))
                # sendReliablyBinary(pickle.dumps(msg),Agent.connection)
                
            else:
                print('something went wrong')
            
        
        return State

    def continueGame(self,State: TeamStateClass):
        """
        Decide whether the game has reached its conclusion.

        Parameters
        ----------
        State : TeamStateClass
            A `StateClass` that has the attribute `Flags: dict`

        Returns
        -------
        bool
            True: Continue game, False: stop game

        """
        # Identify the teams with a FlagCapturer still alive
        TeamsLeft = []
        for Unit in State.Units.values():
            UnitOwner = Unit.Owner
            UnitTeam = self.Agents[UnitOwner].TeamID
            if (UnitTeam not in TeamsLeft) and any([isinstance(Unit,T) for T in self.FlagCapturers]) and Unit.Health !=0:
                TeamsLeft.append(UnitTeam)
                
        return len(TeamsLeft)>1 
        
    def observe(self, State):
        """
        Identify what agents can determine of `State`

        Parameters
        ----------
        State : TeamStateClass
            Ground truth which is observed.

        Returns
        -------
        ObservedStates : dict(dict(set))
            Dictionary collecting observations each agent with `AgentID` has made of state `State` via its units.

        """
        # Identify what each agent can observer
        ObservedStates = defaultdict(lambda: defaultdict(set))
        AgentsUnits = defaultdict(set)
        for Observer in State.Units.values():
            AgentID = Observer.Owner
            for (UnitID, Unit) in State.Units.items():
                # Update list of Unit IDs owned by the agent. 
                #This is needed to ensure that the agents teammates do not corrupt their observations.
                if Unit.Owner == AgentID:
                    AgentsUnits[AgentID].add(UnitID)
                NewUnit = Observer.observe(Unit)
                if NewUnit is not None:
                    NewUnit = self.correctObservation(Observer, Unit, NewUnit)
                    if ObservedStates[AgentID][UnitID] != {NewUnit}:
                        ObservedStates[AgentID][UnitID].add(NewUnit)      
        
        # Update the ObservedState of each agent to include their teammates ObservedState
        for Agent in self.Agents.values():
            if len(ObservedStates.keys()) !=0:
                AgentID = Agent.ID
                AgentTeamID = Agent.TeamID
                for OtherAgent in self.Agents.values():
                    if (AgentID != OtherAgent.ID) and (AgentTeamID == OtherAgent.TeamID):
                        # Only add the units that are not owned by the agent
                        for ObservedUnitID in ObservedStates[OtherAgent.ID].keys():
                            if ObservedUnitID not in AgentsUnits[AgentID]:
                                ObservedStates[AgentID].update({ObservedUnitID: ObservedStates[OtherAgent.ID][ObservedUnitID]})
        
        # For debugging purposes?
        if len(ObservedStates.keys()) == 0:
            print(State)
        return ObservedStates

    def play(self, State: TeamStateClass):
        """
        Play the game starting from `State` and print the result

        Parameters
        ----------
        State : TeamStateClass
            Ground truth which is observed.

        Returns
        -------
        R : Tuple
            A history of the game `State` for each turn

        """
        R = GameClass.play(self, State)
        LastState = R[0]
        TeamsLeft = []
        
        # Identify the teams remaining with a FlagCapturer unit
        for Unit in LastState.Units.values():
            UnitOwner = Unit.Owner
            UnitTeam = self.Agents[UnitOwner].TeamID
            if (UnitTeam not in TeamsLeft) and any([isinstance(Unit,T) for T in self.FlagCapturers]) and Unit.Health !=0:
                TeamsLeft.append(UnitTeam)
        
        # Print the result of the game
        if len(TeamsLeft) == 0:
            msg = "Mutual desctruction"
            print(msg)
        elif len(set([Unit.Owner for Unit in LastState.Units.values() if isinstance(Unit,FlagClass)]))>1:
            msg = "Team %s won since they are the only team with units left" %(TeamsLeft)
            print(msg)
            
        for Agent in self.Agents.values():
            print(type(Agent))
            if isinstance(Agent, RemoteTeamAgentClass):
                print('sending a pickled message from TeamCaptureFlagGameHealth.py line 363')
                Agent.Connection.send(pickle.dumps(msg))
                # sendReliablyBinary(pickle.dumps(msg),Agent.connection)
                
            else:
                print('something went wrong')

            
            
        else:
            msg = "Team %s won!" %(TeamsLeft)
            print(msg)
        
        return R, msg

    def correctObservation(self, Observer, Unit, ObservedUnit):
        """
        Determine the correct observations for the observer.
        E.g., Agent from team 1 can only correctly identify the AgentID and type of a Unit if they are on the same team

        Parameters
        ----------
        Observer : Unit Class
            The Unit making the observation
        Unit : Unit Class
            The Unit being observed
        ObservedUnit : Unit Class
            The observed unit by the Observer

        Returns
        -------
        NewUnit : FlagClass
            A Flag unit with the correct identifiers defined by the game
        ObservedUnit : Unit Class
            A unit with the correct identifiers defined by the game
        """

        # Dead eyes see no future
        if Unit.Health == 0:
            return None
        if any([isinstance(Unit,T) for T in self.ObservableUnits]):#isinstance(Unit, FlagClass):
            AgentID = Observer.Owner
            AgentTeamID = self.Agents[AgentID].TeamID
            NewUnit = Unit.__copy__()
        
            # Set unit owner to None if they are not part of the observers team
            UnitTeamID = self.Agents[NewUnit.Owner].TeamID
            if UnitTeamID != AgentTeamID:
                NewUnit.Owner = None
                NewUnit.ID = None
                return NewUnit
            
        return ObservedUnit
