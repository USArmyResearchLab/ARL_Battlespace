import sys
import errno
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\AgentTypes')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\Games')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\StateTypes')
sys.path.append(r'C:\Users\wpere\Documents\Army\July\dfvc2-Development\src\UnitTypes')

from board import Board
from itertools import cycle
import random
import os
import socket
import pickle
from TeamState import TeamStateClass
from _thread import *
import dill as pickle
import select
from copy import deepcopy
import tkinter as tk
import time
import threading
from RemoteAgent import RemoteTeamAgentClass
from TeamAgents import getUnitAction
import msvcrt


PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
Ledger = {}
board = None
mods = []
PlayerID = 0
remoteActions = []
remoteIDs = []
remoteIDX = 0
contents = ""

def mouse_fn(btn, row, col):    # mouse calback function
    global board
    global PlayerID
    global client
    temp = {}
    temp[PlayerID] = (col,9-row,0)
    msg = pickle.dumps(temp)
    client.send(msg)

def sendMessage(msg, conn):
    message = msg.encode('utf-8')
    conn.send(message)
    print('[Sent] '+msg)

def timer_fn():
    global Ledger
    global PlayerID
    global board
    global client
    global remoteActions
    global remoteIDs
    global remoteIDX
    global contents
    global ActionOptions
    global UnitTypes

    """if msvcrt.kbhit() and contents == "requestActions":
        key = int(msvcrt.getch().decode('utf-8'))
        if key not in range(len(ActionOptions[remoteIDX][1][0])):
            return

        print(key)
        if len(ActionOptions[remoteIDX][1][0])==1:
            Action = ActionOptions[remoteIDX][1][0][0]
            UnitID = ActionOptions[remoteIDX][0]
        else:
            Action = ActionOptions[remoteIDX][1][0][key]
            UnitID = ActionOptions[remoteIDX][0]

        remoteActions.append((UnitID,[Action]))
        remoteIDX += 1
        if remoteIDX >= len(ActionOptions):
            client.send(pickle.dumps(remoteActions))
            contents = ""
            remoteActions = []
            remoteIDX = 0
        else:
            print("Which of the following actions would you like to take for Unit %s?" %(UnitTypes[remoteIDX][1]))
            for ActionCount in range(len(ActionOptions[remoteIDX][1][0])):
                print(ActionCount, " - ",ActionOptions[remoteIDX][1][0][ActionCount])
            print(":")"""

    try:
        inputready, outputready, exceptready = select.select([client], [], [],0)
        for sock in inputready:
            if client == sock:
                data = client.recv(4096)
                if data:
                    data = pickle.loads(data)
                    contents = data["contents"]
                    if data["contents"] == "RemoteAgent":
                        newPosition = data["newPos"]
                        UnitName = data["currMod"]
                        AgentID = data["id"]
                        newOri = data["newOri"]
                        UnitID = data["UnitID"]
                        board[9-newPosition[1]][newPosition[0]] = (newOri,Ledger["Agents"][AgentID]["Units"][UnitID]["ImagePath"])
                        Ledger["Agents"][AgentID]["Units"][UnitID]["Position"] = newPosition
                        if UnitID == max(Ledger["Agents"][AgentID]["Units"]):
                            if AgentID == 2:
                                if PlayerID == 2:
                                    for r in range(board._nrows):
                                        for c in range(board._ncols):
                                            if board._cells[r][c] and r < 5 and c < 5:
                                                board._cells[r][c].bgcolor = "white"
                                elif PlayerID == 3:
                                    for r in range(board._nrows):
                                        for c in range(board._ncols):
                                            if board._cells[r][c] and r < 5 and c >= 5:
                                                board._cells[r][c].bgcolor = "yellow"
                            elif AgentID == 3:
                                for r in range(board._nrows):
                                    for c in range(board._ncols):
                                        if board._cells[r][c] and r < 5 and c >= 5:
                                            board._cells[r][c].bgcolor = "white"

                    elif data["contents"] == "requestActions":
                        PossibleActions = data[0]
                        ActionOptions = list(PossibleActions.items())#[0]
                        #ObservedState = data[1]
                        ActionNames = data[2]
                        UnitTypes = data[3]
                        remoteActions = []
                        remoteIDX = 0
                        Actions = []
                        """UnitTypes = list(UnitTypes.items())
                        print("Which of the following actions would you like to take for Unit %s?" %(UnitTypes[remoteIDX][1]))
                        for ActionCount in range(len(ActionOptions[remoteIDX][1][0])):
                            print(ActionCount, " - ",ActionOptions[remoteIDX][1][0][ActionCount])
                        print(":")"""
                        for UnitID in PossibleActions.keys():
                            Action = (UnitID,[getUnitAction(UnitTypes[UnitID],PossibleActions[UnitID],'',0)])
                            Actions.append(Action)
                        client.send(pickle.dumps(Actions))
                        contents = ""
                        remoteActions = []
                        remoteIDX = 0
                    elif data["contents"] == "updateClient":
                        board.clear()
                        #print(data)
                        for UnitID in data:
                            if UnitID == "contents":
                                continue
                            val = data[UnitID]
                            AgentID = val['AgentID']
                            newPos = val['newPos']
                            newOri = val["newOri"]
                            if UnitID in Ledger["Agents"][AgentID]["Units"]:
                                oldPos = Ledger["Agents"][AgentID]["Units"][UnitID]["Position"]
                                oldOri = Ledger["Agents"][AgentID]["Units"][UnitID]["Orientation"]
                                oldPosition = (int(oldPos[0]),int(oldPos[1]),int(oldPos[2]))
                                newPosition = (int(newPos[0]),int(newPos[1]),int(newPos[2]))
                                #print(AgentID,UnitID,oldPos,oldOri)
                            else:
                                continue
                            board[9-newPosition[1]][newPosition[0]] = (newOri,Ledger["Agents"][AgentID]["Units"][UnitID]["ImagePath"])
                            Ledger["Agents"][AgentID]["Units"][UnitID]["Position"] = newPosition
                            Ledger["Agents"][AgentID]["Units"][UnitID]["Orientation"] = newOri
                        sendMessage('updated',client)

    except socket.error as error:
        if error.errno == errno.ECONNREFUSED:
            print(os.strerror(error.errno))
            board.close()
            client.close()

def random_positions(AgentID):
    global Ledger
    global board
    for x in range(len(Ledger["Agents"][AgentID]["Units"])):
        while 1:
            r = random.randint(0, 9)   # Random row
            c = random.randint(0, 9)    # Random collumn
            if not Ledger["Agents"][AgentID]["Units"][x]["Position"]:                 # It must be an empty place
                Ledger["Agents"][AgentID]["Units"][x]["Position"] = (c,r,0)
                board[r][c] = Ledger["Agents"][AgentID]["Units"][x]["ImagePath"]
                break

def newgame():
    global client
    global board
    global PlayerID
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(client)
    setup = True
    while setup:
        try:
            readable, writable, errored = select.select([client], [], [],0)
            for sock in readable:
                if sock is client:
                    data = client.recv(4096)
                    if data:
                        data = pickle.loads(data)
                        #print(data)
                        if data["contents"] == "PlayerID":
                            PlayerID = data["data"]
                            sendMessage('got it',client)
                        elif data["contents"] == "TeamID":
                            TeamID = data["data"]
                            sendMessage('got it',client)
                        elif data["contents"] == "AgentDict":
                            print(data)
                            for AgentID in data:
                                if AgentID == "contents":
                                    continue
                                for Unit in data[AgentID]:
                                    newPosition = data[AgentID][Unit]["Position"]
                                    newOrientation = data[AgentID][Unit]["Orientation"]
                                    UnitName = Unit
                                    board[9-newPosition[1]][newPosition[0]] = (newOrientation,Ledger["Agents"][AgentID]["Units"][data[AgentID][Unit]["UnitID"]]["ImagePath"])
                                    Ledger["Agents"][AgentID]["Units"][data[AgentID][Unit]["UnitID"]]["Position"] = newPosition
                            setup = False
        except:
            continue

    #time.sleep(1.0)
    if PlayerID == 2:
        for r in range(board._nrows):
            for c in range(board._ncols):
                if board._cells[r][c] and r < 5 and c < 5:
                    board._cells[r][c].bgcolor = "yellow"
    board.start_timer(25)

path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),  "img")
colors = ['blue','green','red','yellow']
modules = ['soldier','truck','tank','plane','flag']
#module_classes = [SoldierClass, TankClass, TruckClass, AirplaneClass, FlagClass]
NumberOfPlayers = 4
NumberOfUnits = [5,5,5,5]
RandomAgentIDs = [0,1,2,3]
#RemoteAgentIDs = [1,2]
TDAgentIDs = []
NumberOfPlayersPerTeam = [2,2]


TeamID = 0
AgentID = 0
UnitID = 0
Ledger["Agents"] = {}
for NumPlayers in NumberOfPlayersPerTeam:
    for Player in range(NumPlayers):
        d = {}
        d["AgentID"] = AgentID
        d["AgentType"] = "Random" if AgentID in RandomAgentIDs else "Remote"
        d["TeamID"] = TeamID
        d["Color"] = colors[AgentID]
        d["Units"] = {}
        Orientation = (0,1,0) if TeamID == 0 else (0,-1,0)
        for NumUnit in range(NumberOfUnits[AgentID]):
            d["Units"][UnitID] = {"Name": modules[NumUnit], "UnitID": UnitID, "Position": (0,0,0), "Orientation": Orientation, "ImagePath": modules[NumUnit]+"-"+colors[AgentID]+".gif"  }
            UnitID += 1

        Ledger["Agents"][AgentID] = d
        AgentID += 1
    TeamID += 1


board = Board(10,10)         # 3 rows, 4 columns, filled w/ None
board.cell_size = 60
board.on_timer = timer_fn
board.on_start = newgame
board.on_mouse_click = mouse_fn
#[random_positions(AgentID) for AgentID in Ledger["Agents"] if Ledger["Agents"][AgentID]["AgentType"] == "Random"]
#print(Ledger)
#if PlayerID == 2:
board.show()
