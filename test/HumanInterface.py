import sys, os
sys.path.append(os.path.realpath('..'))
import errno

import src
from src.UI_Files.board import Board
from itertools import cycle
import itertools
import random
import os
import socket
import pickle
from src.StateTypes.TeamState import TeamStateClass
from _thread import *
import dill as pickle
import select
from copy import deepcopy
import tkinter as tk
import time
import threading
from src.AgentTypes.RemoteAgent import RemoteTeamAgentClass
from src.AgentTypes.TeamAgents import getUnitAction
#import msvcrt
import math
from src.UnitModule import UnitClass
from src.UnitTypes.ExampleUnit import FlagClass
from src.UnitTypes.ProjectileModule import ProjectileClass
from src.UnitTypes.SoldierModule import SoldierClass
from src.UnitTypes.TankModule import TankClass
from src.UnitTypes.TruckModule import TruckClass
from src.UnitTypes.AirplaneModule import AirplaneClass
from src.UnitTypes.WallUnitModule import WallClass
from reliableSockets import sendReliablyBinary, recvReliablyBinary2, emptySocket
import numpy as np
global GameOver

def getIP():
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

PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(getIP())
ADDR = (SERVER, PORT)
print('Your machine\'s IP address is: ',getIP(),'   port: ', PORT)
Ledger = {}
board = None
mods = []
PlayerID = 0
remoteActions = []
remoteIDs = []
remoteIDX = 0
contents = ""

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

def mouse_fn(btn, row, col, verbose = False):    # mouse calback function
    global board
    global PlayerID
    global client
    temp = {}
    temp[PlayerID] = (col,board._nrows-row-1,0)
    msg = pickle.dumps(temp)
    if verbose: print('HumanInterface.py, mouse_fn line 73  sending msg length ',len(msg))
    client.send(msg)

def sendMessage(msg, conn, verbose = False):
    message = msg.encode('utf-8')
    if verbose: print('HumanInterface.py, sendMessage line 78  sending msg length ',len(message))
    conn.send(message)
    if verbose: print('[Sent] '+msg)

def timer_fn(verbose = False):
    verbose = True
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
    global UnitModules
    global TeamColors
    global GameOver

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

    # if GameOver == True:
    #     board.close()
    #     client.close()
    #     return
    try:
        inputready, outputready, exceptready = select.select([client], [], [],0)
        for sock in inputready:
            if client == sock:
                if verbose: print('now in HumanInterface.py, timer_fn, line 123  receiving from client at time ', int(round(time.time() * 1000)))
                data = client.recv(1048576)
                if verbose: print('HumanInterface.py, timer_fn  line 127, received data length ',len(data))
                # if data matches header, send to recvReliablyBinary2
                if (len(data) >= 48):
                    message = data
                    head0 = int.from_bytes(message[0:8], byteorder='big')
                    head1 = int.from_bytes(message[8:16], byteorder='big')
                    head2 = int.from_bytes(message[16:24], byteorder='big')
                    head3 = int.from_bytes(message[24:32], byteorder='big')
                    head4 = int.from_bytes(message[32:40], byteorder='big')
                    head5 = int.from_bytes(message[40:48], byteorder='big')
                    if verbose: print('HumanInterface.py, timer_fn line 139: len(data) >= 48 and int(first 48 bytes) are: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))

                    if int.from_bytes(data[40:48], byteorder='big') == 314159:     # 314159 in bytes 41:48 is a signature of reliableSockets packet header
                        if verbose: print('HumanInterface.py, timer_fn line 142:  this is a reliableSockets packet. Processing with recvReliablyBinary2. len(data) = ',len(data))
                        data = recvReliablyBinary2(client, data)
                        # empty the socket of previous packets for 1 second before continuing
                        emptySocket(client)
                    if ((head0 == 0) and (head1 == 0) and (head2 == 0) and (head3 == 0) and (head4 == 0) and (head5 == 0)):
                        GameOver = True
                        print('HumanInterface.py line 154  received [0 0 0 0 0 0], setting GameOver = True')
                if len(data) == 0:
                    GameOver = True
                    print('HumanInterface.py line 157  len(data) = 0, setting GameOver = True')
                if GameOver:
                    board.clear()
                    # print(data[1])
                    print('Game Over **************************************************************************')
                    GameOver = True
                    board.close()
                    client.close()
                    return
                if data:
                    if verbose: print('data is type ',type(data), 'of length ',len(data))
                    pickleLoadSuccessful = False
                    try:
                        data = pickle.loads(data)
                        pickleLoadSuccessful = True
                    except:
                        print('HumanInterface.py line 156:  Failed to unpickle data at time ',int(round(time.time() * 1000)))
                        print('Ignoring this bad packet.')
                    if pickleLoadSuccessful == True:                   
                        print('HumanInterface.py line 158:  Successful unpickle of data at time ',int(round(time.time() * 1000)))
                        contents = data["contents"]
                        if data["contents"] == "RemoteAgent":
                            #print(data)
                            newPosition = data["newPos"]
                            UnitName = data["currMod"]
                            AgentID = data["id"]
                            newOri = data["newOri"]
                            UnitID = data["UnitID"]
                            board[board._nrows-1-newPosition[1]][newPosition[0]] = (newOri,Ledger["Agents"][AgentID]["Units"][UnitID]["ImagePath"])
                            Ledger["Agents"][AgentID]["Units"][UnitID]["Position"] = newPosition
                            if UnitID == max(Ledger["Agents"][AgentID]["Units"]):
                                if AgentID == 2:
                                    if PlayerID == 2:
                                        for r in range(board._nrows):
                                            for c in range(board._ncols):
                                                if board._cells[r][c] and r < math.floor(board._nrows/2) and c < math.floor(board._ncols/2):
                                                    board._cells[r][c].bgcolor = "white"
                                    elif PlayerID == 3:
                                        for r in range(board._nrows):
                                            for c in range(board._ncols):
                                                if board._cells[r][c] and r < math.floor(board._nrows/2) and c >= math.ceil(board._ncols/2):
                                                    board._cells[r][c].bgcolor = "yellow"
                                elif AgentID == 3:
                                    for r in range(board._nrows):
                                        for c in range(board._ncols):
                                            if board._cells[r][c] and r < math.floor(board._nrows/2) and c >= math.ceil(board._ncols/2):
                                                board._cells[r][c].bgcolor = "white"
    
                        elif data["contents"] == "requestActions":
                            board.clear()
                            #print(data)
                            PossibleActions = data[0]
                            ObservedState = data[1]
                            ActionNames = data[2]
                            UnitTypes = data[3]
                            remoteActions = []
                            remoteIDX = 0
                            Actions = []
                            for UnitID, Unit in ObservedState.items():
                                  UnitOwner = nth(Unit,0).Owner    
                                  TempPos = nth(Unit,0).Position
                                  UnitPosition = ( int(TempPos[0]), int(TempPos[1]), int(TempPos[2]) )
                                  TempOri = nth(Unit,0).Orientation
                                  if TempOri != None:
                                      UnitOrientation = ( int(TempOri[0]), int(TempOri[1]), int(TempOri[2]) )
                                  else:
                                      UnitOrientation = ( 0, 1, 0 )
                                  UnitType = type(nth(Unit,0))
                                  if UnitOwner == None:
                                      UnitColor = 'black'
                                  else:
                                      UnitColor = TeamColors[UnitOwner]
                                  ImagePath = UnitModules[UnitType] + '-' + UnitColor + '.gif'
                                  board[board._nrows-1-UnitPosition[1]][UnitPosition[0]] = (UnitOrientation, ImagePath)
    
                            for UnitID in PossibleActions.keys():
                                #Action = (UnitID,[getUnitAction(UnitTypes[UnitID],PossibleActions[UnitID],'',0)])
                                Action = ( UnitID, [ getUnitAction(UnitTypes[UnitID], PossibleActions[UnitID],'', ActionNames[UnitID]) ] )
                                Actions.append(Action)
                            client.send(pickle.dumps(Actions))
                            contents = ""
                            remoteActions = []
                            remoteIDX = 0
                            print('Actions received and sent to Server. Please wait until next turn.')
                            
                        elif data['contents'] == 'Game Over':
                            board.clear()
                            print(data[1])
                            print('Game Over **************************************************************************')
                            GameOver = True
                            board.close()
                            client.close()

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
            r = random.randint(0, board._nrows)   # Random row
            c = random.randint(0, board._ncols)    # Random collumn
            if not Ledger["Agents"][AgentID]["Units"][x]["Position"]:                 # It must be an empty place
                Ledger["Agents"][AgentID]["Units"][x]["Position"] = (c,r,0)
                board[r][c] = Ledger["Agents"][AgentID]["Units"][x]["ImagePath"]
                break

def newgame():
    global client
    global board
    global PlayerID
    import urllib.request
    global GameOver

    GameOver = False
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    textIn = input('Please provide the IP address of the server, e.g. 71.114.47.132, or press Enter if server and client are on the same machine or router: ')
    if textIn == '':
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        textIn = external_ip
        print('assigning server to same as client, ',external_ip)
    else:
        print(textIn)
    ADDR = (textIn, PORT)    
    client.connect(ADDR)
    print('client: ',client,'  ADDR: ',ADDR)
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
                            sendMessage('got PlayerID',client)
                        elif data["contents"] == "TeamID":
                            TeamID = data["data"]
                            sendMessage('got TeamID',client)
                            setup = False
#                        elif data["contents"] == "AgentDict":
#                            #print(data)
#                            for AgentID in data:
#                                if AgentID == "contents":
#                                    continue
#                                for Unit in data[AgentID]:
#                                    newPosition = data[AgentID][Unit]["Position"]
#                                    newOrientation = data[AgentID][Unit]["Orientation"]
#                                    UnitName = Unit
#                                    board[board._nrows-1-newPosition[1]][newPosition[0]] = (newOrientation,Ledger["Agents"][AgentID]["Units"][data[AgentID][Unit]["UnitID"]]["ImagePath"])
#                                    Ledger["Agents"][AgentID]["Units"][data[AgentID][Unit]["UnitID"]]["Position"] = newPosition
#                                #print(Ledger)
#                            setup = False
        except Exception as e:
            print(e)
            continue

    #time.sleep(1.0)
    if PlayerID == 2:
        print('Please wait for the other player to connect to the server.')
        # timestart = int(round(time.time() * 1000))
        # timeElapsed = int(round(time.time() * 1000)) - timestart
        # allReady = False
        # while (timeElapsed < 20000) and (allReady == False): # 60000 msec
        #     timeElapsed = int(round(time.time() * 1000)) - timestart
        #     data = client.recv(4096)
        #     if data:
        #         print('Ready to start', data)
        #         allReady = True
        # print('Other player has connected. Please place your units and flag by clicking in the yellow area.')
        print('Please WAIT until AFTER the other player has connected. THEN, place your units and flag by clicking in the yellow area.')
        for r in range(board._nrows):
            for c in range(board._ncols):
                if board._cells[r][c] and r < math.floor(board._nrows/2) and c < math.floor(board._ncols/2):
                    board._cells[r][c].bgcolor = "yellow"
    else:
        # data = client.recv(4096)
        # print('Ready to start', data)
        print('Please wait for the other player to place his/her units. When your board turns yellow, place your units and flag in the yellow area.')
    board.start_timer(25)

path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),  "img")
TeamColors = {0: 'blue',
              1: 'green',
              2: 'red',
              3: 'yellow',
              4: 'black',}

UnitModules = {SoldierClass: 'soldier',
               TruckClass: 'truck',
               TankClass: 'tank',
               AirplaneClass: 'plane',
               FlagClass: 'flag',
               WallClass: 'wall',
               ProjectileClass: 'missile',
               UnitClass: 'unknown',}

colors = ['blue','green','red','yellow','black']
modules = ['soldier','truck','tank','plane','flag']
#module_classes = [SoldierClass, TankClass, TruckClass, AirplaneClass, FlagClass]
NumberOfPlayers = 4
NumberOfUnits = [5,5,5,5,9]
RandomAgentIDs = [0,1,2,3]
#RemoteAgentIDs = [1,2]
TDAgentIDs = []
NumberOfPlayersPerTeam = [2,2,1]


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
        if AgentID == 4:
            for NumUnit in range(NumberOfUnits[AgentID]+1):
                d["Units"][UnitID] = {"Name": f'wall{NumUnit}', "UnitID": UnitID, "Position": (0,0,0), "Orientation": Orientation, "ImagePath": "wall-brick.gif"  }
                UnitID += 1
        else:
            for NumUnit in range(NumberOfUnits[AgentID]):
                d["Units"][UnitID] = {"Name": modules[NumUnit], "UnitID": UnitID, "Position": (0,0,0), "Orientation": Orientation, "ImagePath": modules[NumUnit]+"-"+colors[AgentID]+".gif"  }
                UnitID += 1
        
        Ledger["Agents"][AgentID] = d
        AgentID += 1
    TeamID += 1


board = Board(11,10)         # 3 rows, 4 columns, filled w/ None
board.cell_size = 60
board.on_timer = timer_fn
board.on_start = newgame
board.on_mouse_click = mouse_fn
#[random_positions(AgentID) for AgentID in Ledger["Agents"] if Ledger["Agents"][AgentID]["AgentType"] == "Random"]
#print(Ledger)
#if PlayerID == 2:
board.show()
