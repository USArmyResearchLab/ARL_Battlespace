# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 17:15:22 2020

@author: james.z.hare
"""
import sys
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\AgentTypes')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\Games')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\StateTypes')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\UnitTypes')
import socket
from _thread import *
import dill as pickle
from TeamState import TeamStateClass
from TeamCaptureFlagGame import TeamCaptureFlagClass
from TeamAgents import TeamHumanAgentClass, TeamStaticRandomAgentClass, TeamUniformRandomAgentClass
from ExampleUnit import FlagClass
from ProjectileModule import ProjectileClass
from SoldierModule import SoldierClass
from TankModule import TankClass
from TruckModule import TruckClass
from AirplaneModule import AirplaneClass
from copy import deepcopy
import random
import time
from datetime import datetime
from RemoteAgent import RemoteTeamAgentClass
#from TeamCaptureFlagGameHealth import TeamCaptureFlagHealthClass
from TeamAnnihilationGameHealth import TeamAnnihilationGameClass
import enum
import sys
import json
import select

if len(sys.argv) >= 2:
    GameType = sys.argv[1]
    if GameType not in ['--train','--test']:
        print("Specify Game Type: --train or --test")
        sys.exit()
else:
    print("Specify Game Type: --train or --test")
    sys.exit()

modules = ['Soldier','Truck','Tank','Airplane','Flag']
UnitClasses = [SoldierClass,TruckClass, TankClass, AirplaneClass, FlagClass]
idCount = 0
ReadyPlayers = 0
NumberOfPlayers = 4
aPositions = {}
mTurn = 0
NumberOfPlayersPerTeam = [2,2]

NumberOfUnits = [5,5,5,5]
State0 = TeamStateClass()
GameDic = {}
AgentDict = {}
State0.FlagPosition = {}
State0.BoardSize = ( 10,10,2 )
# Define the section of the board that each player may place their units
TwoPlayerCord = ( ((0,State0.BoardSize[0]/2-1),(0,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(0,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]/2-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

TwoPlayerCordUnits = ( ((0,State0.BoardSize[0]/2-1),(State0.BoardSize[1]/2-3,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(State0.BoardSize[1]/2-1,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]/2-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

TwoPlayerCordFlag = ( ((0,State0.BoardSize[0]/2-1),(0,State0.BoardSize[1]/2-4),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(0,State0.BoardSize[1]/2-4),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]/2-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((State0.BoardSize[0]/2,State0.BoardSize[0]-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

OnePlayerCord = ( ((0,State0.BoardSize[0]-1),(0,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

OnePlayerCordUnits = ( ((0,State0.BoardSize[0]-1),(State0.BoardSize[1]/2-3,State0.BoardSize[1]/2-1),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]-1),(State0.BoardSize[1]/2,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

OnePlayerCordFlag = ( ((0,State0.BoardSize[0]-1),(0,State0.BoardSize[1]/2-4),(0,State0.BoardSize[2]-1)),
               ((0,State0.BoardSize[0]-1),(State0.BoardSize[1]/2+3,State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

def placeRandomUnits(PlayerID, NumberOfUnits, UnitsCord, FlagCord):
    global State0
    global AgentDict
    while True:
        SoldierPos = ( random.randint(UnitsCord[PlayerID][0][0],UnitsCord[PlayerID][0][1]),
                      random.randint(UnitsCord[PlayerID][1][0],UnitsCord[PlayerID][1][1]),
                      0 )
        TruckPos = ( random.randint(UnitsCord[PlayerID][0][0],UnitsCord[PlayerID][0][1]),
                      random.randint(UnitsCord[PlayerID][1][0],UnitsCord[PlayerID][1][1]),
                      0 )
        TankPos = ( random.randint(UnitsCord[PlayerID][0][0],UnitsCord[PlayerID][0][1]),
                      random.randint(UnitsCord[PlayerID][1][0],UnitsCord[PlayerID][1][1]),
                      0 )
        if SoldierPos != TruckPos and SoldierPos != TankPos and TruckPos != TankPos:
            break

    AirplanePos = ( random.randint(UnitsCord[PlayerID][0][0],UnitsCord[PlayerID][0][1]),
                  random.randint(UnitsCord[PlayerID][1][0],UnitsCord[PlayerID][1][1]),
                  1 )
    FlagPos = ( random.randint(FlagCord[PlayerID][0][0],FlagCord[PlayerID][0][1]),
               random.randint(FlagCord[PlayerID][1][0],FlagCord[PlayerID][1][1]),
               0 )
    # Add the unit to the state
    State0.Units[(PlayerID*5 + 0)] = SoldierClass((PlayerID*5 + 0),PlayerID,Position=SoldierPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Soldier'] = {"UnitID":PlayerID*5, "Position": SoldierPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 1)] = TruckClass((PlayerID*5 + 1),PlayerID,Position=TruckPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Truck'] = {"UnitID":PlayerID*5+1, "Position": TruckPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 2)] = TankClass((PlayerID*5 + 2),PlayerID,Position=TankPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Tank'] = {"UnitID":PlayerID*5+2, "Position": TankPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 3)] = AirplaneClass((PlayerID*5 + 3),PlayerID,Position=AirplanePos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Airplane'] = {"UnitID":PlayerID*5+3, "Position": AirplanePos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 4)] = FlagClass((PlayerID*5 + 4),PlayerID,Position=FlagPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Flag'] = {"UnitID":PlayerID*5+4, "Position": FlagPos, "Orientation":(0,1,0)}
    State0.FlagPosition[PlayerID] = FlagPos
    print(SoldierPos,TruckPos,TankPos,AirplanePos,FlagPos)

def broadcast(msg):  # prefix is for name identification.
    for id in Connections:
        Connections[id].send(msg)

def sendMessage(msg, conn):
    message = msg.encode('utf-8')
    conn.send(message)
    print('[Sent] '+msg, conn)

def initPositions(conn, PlayerID, TeamID, FlagPositions):
    global idCount
    global ReadyPlayers
    global State0
    global mTurn
    global aPositions
    global AgentDict
    counter = 0
    AgentDict[PlayerID] = {}
    x = {"contents":"PlayerID","data":PlayerID}
    conn.send(pickle.dumps(x))
    init = True
    while init:
        try:
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    data = conn.recv(2048).decode('utf-8')
                    print('[Received] '+data)
                    x = {"contents":"TeamID","data":TeamID}
                    conn.send(pickle.dumps(x))
                    init = False
                    break
        except:
            continue

    init = True
    while init:
        try:
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    data = conn.recv(2048).decode('utf-8')
                    print('[Received] '+data)
                    AgentDict["contents"] = "AgentDict"
                    msg = pickle.dumps(AgentDict)
                    broadcast(msg)
                    #conn.send(msg)
                    init = False
                    break
        except:
            continue

    init = True
    while init:
        try:
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    data = conn.recv(1024)
                    # Check if a message was received from the Client
                    if data:
                        data = pickle.loads(data)
                        print(data)
                        UnitID = list(data.keys())[0]
                        Position = data[UnitID]
                        UnitID = UnitID*5 + mTurn
                        curr_mod = modules[mTurn]
                        if mTurn == 4:
                            mTurn = 0
                        else:
                            mTurn += 1
                        next_mod = modules[mTurn]
                        newPos = Position
                        oldPos = aPositions[PlayerID][curr_mod]
                        if TeamID == 0 or curr_mod == "Flag":
                            Ori = (0,1,0)
                        else:
                            Ori = (0,-1,0)
                        d = {"id":PlayerID, "UnitID": UnitID, "currMod": curr_mod, "nextMod": next_mod, "oldPos": oldPos, "newPos":newPos, "newOri":Ori,"contents":"RemoteAgent" }
                        msg = pickle.dumps(d)
                        broadcast(msg)
                        aPositions[PlayerID][curr_mod] = newPos
                        if counter == 0:
                            State0.Units[(PlayerID*5 + 0)] = SoldierClass((PlayerID*5 + 0),PlayerID,Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Soldier'] = {"UnitID":(PlayerID*5 + 0), "Position": newPos, "Orientation":Ori}
                        elif counter == 1:
                            State0.Units[(PlayerID*5 + 1)] = TruckClass((PlayerID*5 + 1),PlayerID,Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Truck'] = {"UnitID":(PlayerID*5 + 1), "Position": newPos, "Orientation":Ori}
                        elif counter == 2:
                            State0.Units[(PlayerID*5 + 2)] = TankClass((PlayerID*5 + 2),PlayerID,Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Tank'] = {"UnitID":(PlayerID*5 + 2), "Position": newPos, "Orientation":Ori}
                        elif counter == 3:
                            State0.Units[(PlayerID*5 + 3)] = AirplaneClass((PlayerID*5 + 3),PlayerID,Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Airplane'] = {"UnitID":(PlayerID*5 + 3), "Position": newPos, "Orientation":Ori}
                        elif counter == 4:
                            State0.Units[(PlayerID*5 + 4)] = FlagClass((PlayerID*5 + 4),PlayerID,Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Flag'] = {"UnitID":(PlayerID*5 + 4), "Position": newPos, "Orientation":Ori}
                            State0.FlagPosition[(PlayerID)] = newPos
                            ReadyPlayers += 1
                            counter = 0
                            break
                        counter += 1
            else:
                continue  # only executed if the inner loop did NOT break
            break
        except:
            if ReadyPlayers == NumberOfPlayers:
                break

    while Game.GameOn == 0:
        if ReadyPlayers == NumberOfPlayers:
            Game.GameOn = 1

    return State0 # This might be redundant?

def sendResult(conn, Result):
    conn.send(pickle.dumps(Result))

def build_board(BoardSize):
    board = []
    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            board.append(str(i)+', '+str(j))
    return board

land_acts = {'doNothing': -0.1,
   'turn-135': 0,
   'turn-90': 0,
   'turn-45': 0,
   'turn0': 0,
   'turn45': 0,
   'turn90': 0,
   'turn135': 0,
   'turn180': 0,
   'advance1': 0.00,
   'shoot': 0,
   'ram': 0.00}
air_acts = {'doNothing': 0,
'turn-135': 0,
'turn-90': 0,
'turn-45': 0,
'turn0': 0,
'turn45': 0,
'turn90': 0,
'turn135': 0,
'turn180': 0,
'advance0,-2': 0.9/12,
'advance-1,-1': 0.9/12,
'advance0,-1': 0.9/12,
'advance1,-1': 0.9/12,
'advance-2,0': 0.9/12,
'advance-1,0': 0.9/12,
'advance0,0': 0,
'advance1,0': 0.9/12,
'advance2,0': 0.9/12,
'advance-1,1': 0.9/12,
'advance0,1': 0.9/12,
'advance1,1': 0.9/12,
'advance0,2': 0.9/12,
'ascend': 0,
'descend': 0,
'shoot': 0.05,
'bomb': 0.05}

board = build_board(State0.BoardSize)
QTable = {}
QTable["land"] = {}
QTable["air"] = {}
orientations = ["0, 1","0, -1","1, 0","-1, 0","1, 1","1, -1","-1, 1","-1, -1"]
#populates value table
for state in board:
    QTable["land"][state] = {}
    for orient in orientations:
        QTable["land"][state][orient] = land_acts.copy()
for state in board:
    QTable["air"][state] = {}
    for orient in orientations:
        QTable["air"][state][orient] = air_acts.copy()

eps = -1
if GameType == '--test':
    eps = 0
    f = open('QTable.json')
    QTable = json.load(f)
elif GameType == '--train':
    eps = 0.3

TDAgentIDs = []
RandomAgentIDs = [0,1]
for RandomAgent in RandomAgentIDs:
    AgentDict[idCount] = {}
    if idCount < NumberOfPlayersPerTeam[0]:
        TeamID = 0
    else:
        TeamID = 1
    #GameDic[idCount] = TeamTDAgentClass(idCount,TeamID,QTable, None, eps)
    GameDic[idCount] = TeamUniformRandomAgentClass(idCount, TeamID)
    if NumberOfPlayersPerTeam[TeamID] == 1:
        placeRandomUnits(idCount, NumberOfUnits[idCount], OnePlayerCord, OnePlayerCordFlag)
    if NumberOfPlayersPerTeam[TeamID] == 2:
        placeRandomUnits(idCount, NumberOfUnits[idCount], TwoPlayerCord, TwoPlayerCordFlag)
    ReadyPlayers += 1
    idCount += 1

def resetGame(QT,eps):
    NewState0 = InitialState
    for idCount in [0,1]:
        NewGameDic[idCount] = TeamUniformRandomAgentClass(idCount,0)
    for idCount in [2,3]:
        #NewGameDic[idCount] = RemoteTeamAgentClass(idCount, 1, TeamHumanAgentClass, None, None, GameType)
        NewGameDic[idCount] = TeamUniformRandomAgentClass(idCount, 1)
    NewGame = TeamCaptureFlagClass(NewGameDic)
    NewGame.type = GameType
    NewState0.Players = range(len(NewGame.Agents))
    eps -= 0.001
    return NewGame,NewState0,eps

if GameType == '--train':
    RandomAgentIDs = [2,3]
    RemoteAgentIDs = []
    for Agent in RandomAgentIDs:
        AgentDict[idCount] = {}
        if idCount < NumberOfPlayersPerTeam[0]:
            TeamID = 0
        else:
            TeamID = 1
        #GameDic[idCount] = RemoteTeamAgentClass(idCount, TeamID, TeamHumanAgentClass, None, None, GameType)
        GameDic[idCount] = TeamUniformRandomAgentClass(idCount, TeamID)
        if NumberOfPlayersPerTeam[TeamID] == 1:
            placeRandomUnits(idCount, NumberOfUnits[idCount], OnePlayerCord, OnePlayerCordFlag)
        if NumberOfPlayersPerTeam[TeamID] == 2:
            placeRandomUnits(idCount, NumberOfUnits[idCount],TwoPlayerCord, TwoPlayerCordFlag)
        ReadyPlayers += 1
        idCount += 1
    #Game = TeamCaptureFlagHealthClass(GameDic)
    Game = TeamCaptureFlagClass(GameDic)
    State0.Players = range(len(Game.Agents))
    Game.type = GameType
    Game.AgentIDs = {"TDAgentIDs":TDAgentIDs,"RandomAgentIDs": RandomAgentIDs,"RemoteAgentIDs":RemoteAgentIDs}
    Game.caller = "Server"
    InitialState = deepcopy(State0)
    NewGameDic = {}
    NumIters = 50
    score = {}
    for i in range(NumIters):
        print("\nGame Iteration:",i)
        R = Game.play(State0)
        QT = R[1]
        TeamsLeft = R[2]
        if TeamsLeft:
            TeamsLeft = TeamsLeft[0]
            if TeamsLeft not in score:
                score[TeamsLeft] = 1
            else:
                score[TeamsLeft] += 1

        Game,State0,eps = resetGame(QT,eps)
    print("TD Agents Won",score[0],'/50 games')

elif GameType == '--test':
    RandomAgentIDs = []
    RemoteAgentIDs = [2,3]
    Server = socket.gethostbyname(socket.gethostname())
    Port = 5050
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((Server, Port))
    except socket.error as e:
        str(e)

    s.setblocking(0)
    s.listen(2)
    print("Waiting for a connection, Server Started")
    Connections = {}
    Addresses = {}
    init = True
    while init:
        try:
            readable, writable, errored = select.select([s], [], [],0)
            for sock in readable:
                if sock is s:
                    conn, addr = s.accept()
                    print("Connected to:", addr)
                    print(conn)
                    conn.setblocking(1)
                    PlayerID = idCount
                    aPositions[PlayerID] = {}
                    for mod in ['Soldier','Truck','Tank','Airplane','Flag']:
                        aPositions[PlayerID][mod] = (0,0,0)
                    Connections[PlayerID] = conn
                    Addresses[PlayerID] = addr
                    if PlayerID < NumberOfPlayersPerTeam[0]:
                        TeamID = 0
                    else:
                        TeamID = 1
                    GameDic[PlayerID] = RemoteTeamAgentClass(PlayerID, TeamID, TeamHumanAgentClass, None)
                    idCount += 1
                    if idCount == NumberOfPlayers:
                        #Game = TeamCaptureFlagHealthClass(GameDic)
                        Game = TeamCaptureFlagClass(GameDic)
                        Game.caller = "Server"
                        Game.AgentIDs = {"TDAgentIDs":TDAgentIDs,"RandomAgentIDs": RandomAgentIDs,"RemoteAgentIDs":RemoteAgentIDs}
                        State0.Players = range(len(Game.Agents))
                        for Agent in GameDic.values():
                            if isinstance(Agent,RemoteTeamAgentClass):
                                ID = Agent.ID
                                Agent.Connection = Connections[ID]
                                Game.Agents[ID] = Agent
                                print('Updated Agent',ID,'with connection', Agent.Connection)
                        print("Creating new game...")
                    start_new_thread(initPositions, (conn, PlayerID, TeamID,QTable["FlagPositions"]))
                    if idCount == NumberOfPlayers:
                        init = False
        except:
            if idCount == NumberOfPlayers:
                init = False
            else:
                continue


    while Game.GameOn == 0:
        if Game.GameOn == 1:
            break

    print("STARTING GAME")
    time.sleep(3)
    Game.type = GameType
    R = Game.play(State0)
    print(R[2])
    while 1:
        continue
