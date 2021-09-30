
from src.AgentModule import AgentClass
from src.AgentTypes.HumanAgent import HumanAgentClass
from src.AgentTypes.TeamAgents import TeamHumanAgentClass
import itertools
import socket
from _thread import *
import dill as pickle
import errno
import select
from reliableSockets import sendReliablyBinary, recvReliablyBinary2, emptySocket


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

class RemoteAgentClass(AgentClass):
    def __init__(self, ID, ClassType, Connection):
        ClassType.__init__(self, ID)
        #self = ClassType(ID)
        self.Connection = Connection

    def updateDecisionModel(self, Observations, PriorActions):
        pass


class RemoteTeamAgentClass(AgentClass):
    def __init__(self, ID, TeamID, ClassType, Connection):
        self.AgentType = ClassType(ID, TeamID)
        self.Connection = Connection
        self.ID = ID
        self.TeamID = TeamID
        self.Actions = {}
        self.Went = 0
        self.Updated = 0

    def getActions(self, ObservedState, State):
        #msg = self.AgentType.printObservedState(ObservedState)
        ActionOptions = {}
        ActionNames = {}
        UnitTypes = {}
        for UnitID, Units in ObservedState.items():
            if len(Units)==1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0)
                ActionOptions[UnitID] = Unit.possibleActions(State)
                UnitTypes[UnitID] = type(Unit)
                UnitActionNames = ()
                for Action in ActionOptions[UnitID][0]:
                    ActionResult = Unit.Actions[Action](State)
                    ActionName = Action
                    if 'advance' in Action:
                        ActionName = 'Advance to '+str(ActionResult[1].Position)
                    if 'turn' in Action:
                        ActionName = 'Change Orientation to '+str(ActionResult[1].Orientation)
                    if 'ram' in Action:
                        ActionName = 'Ram square '+str(ActionResult[1].Position)
                    UnitActionNames += (ActionName,)
                ActionNames.update({UnitID: (UnitActionNames,)})
        return {0: ActionOptions, 1: ObservedState, 2: ActionNames, 3: UnitTypes }

    def requestActions(self, conn, PossibleActions):
        """
        Get the Actions for each unit from the Client `conn`

        Parameters
        ----------
        conn: [socket]
            Client
        PossibleActions: [dict]
            A Dictionary with key `0` containing the available actions for each unit
            and key `1` containing a string of the Clients `ObservedState`
        """
        self.Went = 0
        PossibleActions["contents"] = "requestActions"
        print('now in RemoteAgent.py, requestActions, line 77  sending PossibleActions   length ',len(pickle.dumps(PossibleActions)))
        # conn.send(pickle.dumps(PossibleActions))    # data size is about 18504 bytes?
        sendReliablyBinary(pickle.dumps(PossibleActions),conn)

        while True:
            try:
                print('now in RemoteAgent.py, requestActions, line 81  receiving AgentAction')
                data = conn.recv(1024)  # this line does not complete until all actions are selected for this player and the data is sent/received
                print('size of data received is: ', len(data))   # data size is about 127 bytes
                if data:
                    AgentAction = pickle.loads(data)
                    print(AgentAction)
                    break
            except socket.error as error:
                if error.errno == errno.ECONNREFUSED:
                    print(os.strerror(error.errno))
                    board.close()
                    client.close()
                else:
                    print(error)

        self.Went = 1
        self.Actions = AgentAction

    def chooseActions(self, ObservedState, State):
        self.Went = 0
        PossibleActions = self.getActions(ObservedState, State)
        #print(PossibleActions[0])
        #print(self.Connection)
        start_new_thread(self.requestActions, (self.Connection, PossibleActions))
        while self.Went == 0:
            pass
        return self.Actions

    def updateClient(self,NewUnits):
        self.Updated = 0
        d = {}
        for Unit in NewUnits:
            AgentID = Unit.Owner
            newPosition = Unit.Position
            newOrientation = Unit.Orientation
            d[Unit.ID] = {"AgentID":AgentID, "UnitID": Unit.ID, "newPos":newPosition, "newOri":newOrientation}
        d["contents"] = "updateClient"
        print('now in RemoteAgent.py, updateClient, line 118  sending request to updateClient')
        self.Connection.send(pickle.dumps(d))
        while True:
            try:
                print('now in RemoteAgent.py, updateClient, line 122  receiving AgentAction')
                data = self.Connection.recv(2048).decode('utf-8')
                print('size of data received is: ', len(data))
                if data:
                    print(data)
                    break
            except Exception as e:
                print('Error', e)
        self.Updated = 1

    def updateDecisionModel(self, Observations, PriorActions):
        pass
