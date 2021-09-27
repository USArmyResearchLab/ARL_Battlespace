# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 17:15:22 2020

@author: james.z.hare
"""
import sys, os
sys.path.append(os.path.realpath('..'))

import socket
from _thread import *
import dill as pickle

import src
from src.StateTypes.TeamState import TeamStateClass
from src.Games.TeamCaptureFlagGame import TeamCaptureFlagClass
from src.AgentTypes.TeamAgents import TeamHumanAgentClass, TeamStaticRandomAgentClass, TeamUniformRandomAgentClass
from src.UnitTypes.ExampleUnit import FlagClass
from src.UnitTypes.ProjectileModule import ProjectileClass
from src.UnitTypes.SoldierModule import SoldierClass
from src.UnitTypes.TankModule import TankClass
from src.UnitTypes.TruckModule import TruckClass
from src.UnitTypes.AirplaneModule import AirplaneClass
from src.UnitTypes.WallUnitModule import WallClass
from copy import deepcopy
import random
import time
from datetime import datetime
from src.AgentTypes.RemoteAgent import RemoteTeamAgentClass
#from TeamCaptureFlagGameHealth import TeamCaptureFlagHealthClass
from src.Games.TeamAnnihilationGameHealth import TeamAnnihilationGameClass
import enum
import sys
import json
import select
import math
from reliableSockets import sendReliablyBinary, recvReliablyBinary2, emptySocket
from src.CSVOutputModule import getAgentObservations

if len(sys.argv) >= 2:
    GameType = sys.argv[1]
    if GameType not in [ '--train', '--test' ]:
        print("Specify Game Type: --train or --test")
        sys.exit()
else:
    print("Specify Game Type: --train or --test")
    sys.exit()

modules = [ 'Soldier', 'Truck', 'Tank', 'Airplane', 'Flag', 'Wall' ]
UnitClasses = [ SoldierClass, TruckClass, TankClass, AirplaneClass, FlagClass, WallClass ]
idCount = 0
ReadyPlayers = 0
NumberOfPlayers = 4
aPositions = {}
mTurn = 0
NumberOfPlayersPerTeam = [ 2, 2 ]
Health = 1

NumberOfUnits = [ 5, 5, 5, 5 ]
State0 = TeamStateClass()
GameDic = {}
AgentDict = {}
State0.FlagPosition = {}
State0.BoardSize = ( 10, 11, 2 )
# Define the section of the board that each player may place their units
TwoPlayerCord = ( ((0,math.floor(State0.BoardSize[0]/2-1)),(0,math.floor(State0.BoardSize[1]/2-1)),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(0,math.floor(State0.BoardSize[1]/2)-1),(0,State0.BoardSize[2]-1)),
               ((0,math.floor(State0.BoardSize[0]/2-1)),(math.ceil(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(math.ceil(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

TwoPlayerCordUnits = ( ((0,math.floor(State0.BoardSize[0]/2-1)),(math.floor(State0.BoardSize[1]/2)-3,math.floor(State0.BoardSize[1]/2)-1),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(math.floor(State0.BoardSize[1]/2)-1,math.floor(State0.BoardSize[1]/2)-1),(0,State0.BoardSize[2]-1)),
               ((0,math.floor(State0.BoardSize[0]/2)-1),(math.floor(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(math.ceil(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
             )

TwoPlayerCordFlag = ( ((0,math.floor(State0.BoardSize[0]/2)-1),(0,math.floor(State0.BoardSize[1]/2)-4),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(0,math.floor(State0.BoardSize[1]/2)-4),(0,State0.BoardSize[2]-1)),
               ((0,math.floor(State0.BoardSize[0]/2)-1),(math.floor(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1)),
               ((math.ceil(State0.BoardSize[0]/2),State0.BoardSize[0]-1),(math.ceil(State0.BoardSize[1]/2),State0.BoardSize[1]-1),(0,State0.BoardSize[2]-1))
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

def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP




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
    State0.Units[(PlayerID*5 + 0)] = SoldierClass((PlayerID*5 + 0),PlayerID, Health, Position=SoldierPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Soldier'] = {"UnitID":PlayerID*5, "Position": SoldierPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 1)] = TruckClass((PlayerID*5 + 1),PlayerID, Health, Position=TruckPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Truck'] = {"UnitID":PlayerID*5+1, "Position": TruckPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 2)] = TankClass((PlayerID*5 + 2),PlayerID, Health, Position=TankPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Tank'] = {"UnitID":PlayerID*5+2, "Position": TankPos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 3)] = AirplaneClass((PlayerID*5 + 3),PlayerID, Health, Position=AirplanePos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Airplane'] = {"UnitID":PlayerID*5+3, "Position": AirplanePos, "Orientation":(0,1,0)}
    State0.Units[(PlayerID*5 + 4)] = FlagClass((PlayerID*5 + 4),PlayerID, Health, Position=FlagPos, Orientation=(0,1,0))
    AgentDict[PlayerID]['Flag'] = {"UnitID":PlayerID*5+4, "Position": FlagPos, "Orientation":(0,1,0)}
    State0.FlagPosition[PlayerID] = FlagPos
    print(SoldierPos,TruckPos,TankPos,AirplanePos,FlagPos)

def broadcast(msg, verbose = False):  # prefix is for name identification.
    for id in Connections:
        if verbose: print('now in ServerWithUI.py, broadcast, line 150   broadcasting msg of length ', len(msg))   # length of this message is about 190 bytes
        Connections[id].send(msg)

def sendMessage(msg, conn, verbose = False):
    message = msg.encode('utf-8')
    if verbose: print('now in ServerWithUI.py, sendMessage, line 155   sending msg of length ', len(message))
    conn.send(message)
    if verbose: print('[Sent] '+msg, conn)

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
    print('now in ServerWithUI, initPositions, line 167  sending contents = data : PlayerID = PlayerID   length ',len(pickle.dumps(x)))
    conn.send(pickle.dumps(x))
    init = True
    while init:
        try:
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    print('now in ServerWithUI, initPositions, line 177  receiving data')   # size of data received is about 10-12 bytes
                    data = conn.recv(2048).decode('utf-8')
                    print('size of data received is: ', len(data))
                    print('[Received] '+data)
                    x = {"contents":"TeamID","data":TeamID}
                    print('now in ServerWithUI, initPositions, line 182  sending TeamID   length ',len(pickle.dumps(x)))   # length is about 49 bytes
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
                    print('now in ServerWithUI, initPositions, line 196  receiving data')
                    data = conn.recv(1024)
                    print('size of data received is: ', len(data))   # length of data received is about 18 bytes
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
                            State0.Units[(PlayerID*5 + 0)] = SoldierClass((PlayerID*5 + 0),PlayerID, Health, Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Soldier'] = {"UnitID":(PlayerID*5 + 0), "Position": newPos, "Orientation":Ori}
                        elif counter == 1:
                            State0.Units[(PlayerID*5 + 1)] = TruckClass((PlayerID*5 + 1),PlayerID, Health, Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Truck'] = {"UnitID":(PlayerID*5 + 1), "Position": newPos, "Orientation":Ori}
                        elif counter == 2:
                            State0.Units[(PlayerID*5 + 2)] = TankClass((PlayerID*5 + 2),PlayerID, Health, Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Tank'] = {"UnitID":(PlayerID*5 + 2), "Position": newPos, "Orientation":Ori}
                        elif counter == 3:
                            State0.Units[(PlayerID*5 + 3)] = AirplaneClass((PlayerID*5 + 3),PlayerID, Health, Position=newPos, Orientation=Ori)
                            AgentDict[PlayerID]['Airplane'] = {"UnitID":(PlayerID*5 + 3), "Position": newPos, "Orientation":Ori}
                        elif counter == 4:
                            State0.Units[(PlayerID*5 + 4)] = FlagClass((PlayerID*5 + 4),PlayerID, Health, Position=newPos, Orientation=Ori)
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
    
GapLocation = (4,5,0)
GameDic[NumberOfPlayers] = TeamUniformRandomAgentClass(NumberOfPlayers,2)
NumUnits = sum(NumberOfUnits)
AgentDict[NumberOfPlayers] = {}
for Boulder in range(State0.BoardSize[0]):
    if Boulder != GapLocation[0]:
        State0.Units[NumUnits + Boulder] = WallClass(NumUnits+Boulder, NumberOfPlayers, 1, Position=(Boulder, GapLocation[1], GapLocation[2]), Orientation=(0,1,0))
        AgentDict[NumberOfPlayers][f'Wall{Boulder}'] = {"UnitID":NumUnits + Boulder, "Position": (Boulder, GapLocation[1], GapLocation[2]), "Orientation":(0,1,0)}

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

def sendResult(conn, Result):
    """
    Transmits the `Result` to the connection `conn`

    Parameters
    ----------
    conn: [socket class]
        Client that the message will be sent to
    Result: [str]
        Game result
    """
    print('now in ServerWithUI, sendResult, line 371  sending pickled Result')
    conn.send(pickle.dumps(Result))
    print("Game Over.  Press Ctrl-C to exit.")
    conn.close()

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
    
    print('This version of GUI is meant for reliable server and client communication through an external network.')

    import urllib.request
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    print('Your router\'s external IP address is: ',external_ip)
    print('and your server\'s local IP address is: ',getIp())
    print('Please configure your router\'s Port Forwarding so that port 5050 is forwarded to ',getIp())
            
    Server = socket.gethostbyname(getIp())
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
                    print('raddr is: ',addr[0],' port ',addr[1])
                    
                    conn.setblocking(1)
                    PlayerID = idCount
                    aPositions[PlayerID] = {}
                    for mod in modules:
                        aPositions[PlayerID][mod] = (0,0,0)
                    Connections[PlayerID] = conn
                    Addresses[PlayerID] = addr
                    print('The address of this player is: ',Addresses[PlayerID][0],'  port ',Addresses[PlayerID][1])
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
    
    # Save the Game Logs
    GameHistory = {}
    GameHistory['StateLog'] = R[0][1]#StateLog
    GameHistory['AgentActions'] = R[0][2]#Game.AgentActions
    GameHistory['AgentObservationLogs'] = R[0][3]#Game.AgentObservationLogs
    GameHistory['GameResult'] = R[1]#msg
    
    
    # Let the Clients know the game result
    for PlayerID in Connections.keys():
        data = {1: R[1],
                'contents': 'Game Over'}
        start_new_thread(sendResult, ( Connections[PlayerID], data ) )   
        
    now = datetime.now()
    DateTimeString = now.strftime("%b_%d_%Y_%H_%M_%S")
    FileName = f"Team0_{NumberOfPlayersPerTeam[0]}Commanders_Team1_{NumberOfPlayersPerTeam[1]}Commanders_{DateTimeString}.csv"
    
    Out = getAgentObservations(GameHistory, GameDic, FileName)
    
    print(R[2])
    while 1:
        continue
