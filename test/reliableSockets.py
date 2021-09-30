#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 12:56:27 2021

@author: chou.p.hung
"""
import dill as pickle
import struct
import numpy as np
import time
import socket
global GameOver


def toEightBytes(number):
    # e.g. converts 8 to b'\x00\x00\x00\x00\x00\x00\x00\x08'
    # print('reliableSockets.py, toEightBytes line 15, type of number was ',type(number))
    if type(number) == np.int64:
        intNumber = number.item()
        number = intNumber
        # eight_bytes = number.to_bytes(8, byteorder='big', signed = True)
        # print('type of number was np.int64. It is now ',type(eight_bytes))                
    if type(number) == int:
        eight_bytes = number.to_bytes(8, byteorder='big')   #     eight_bytes = number.to_bytes(8, byteorder='big', signed = True)
        # print('type of number is now ',type(eight_bytes))                        
    return eight_bytes

def sendReliablyBinary(msg, conn, verbose = False):
    verbose = True
    import math, random, copy, select
    wholePacketSize = 1048
    dataPacketSize = wholePacketSize - 48 # HEADER: Reserve the first 48 bytes of each packet as six INT64s. 
                                          #  The 1st INT64 indicates number of remaining packets (N ... 1)
                                          #  The 2nd INT64 indicates the total number of packets for this message
                                          #  The 3rd INT64 indicates the wholePacketSize of the last packet in this message
                                          #  Define the remaining 3 INT64s as x, y, and 314159 for error-checking. 
                                          # For the 1st INT64, a value of 0 indicates that this packet is for server-client handshaking.
                                          #   Handshaking packets are only 48 bytes long.
                                          #   E.g. If a sender sends a packet of [0, 73, 736, x, y, 314159],
                                          #   it would tell the recipient to expect 73 packets, where the last packet has a wholePacketSize of 736.
                                          #    x would be a random number for SYN (if this is the sender), or the SequenceNumber (if this is the recipient)
                                          #    y would be the ACK, which is 1 + x of the last packet received from the counterparty
                                          # The recipient would then send [0, 73, 736, SeqNum, x+1, 314159] to signal receipt and readiness
                                          # The sender would then send    [1, 73, 736, x+1, SeqNum+1, 314159, {2k bytes of data}]
                                          #  and the next packet would be [2, 73, 736, x+2, SeqNum+1, 314159, {2k bytes of data}]
                                          # Upon receipt of packet 73, the recipient sends [-1, 73, 736, 0, 0, 314159] to indicate successful completion
                                          # At any time, recipient can send [packet_num, 73, 736, 314159, 314159, 314159] to request resend packet_num
    pickledData = msg   # message is already pickled
    dataSize = len(pickledData)
    numPacketsToSend = math.ceil(dataSize / dataPacketSize)
    lastPacketSize = (dataSize % dataPacketSize) + 48
    if verbose: print('lastPacketSize should be ',lastPacketSize)
        
    initialPacketRecvd = False
    SYN = random.randrange(1000000,1000000000)

    while (initialPacketRecvd == False): # THIS IS THE LOOP FOR SENDING an initial SYN PACKET
        # send initial packet for SYN
        head0 = toEightBytes(0)   # 0 indicates that this is the initial packet for SYN
        head1 = toEightBytes(numPacketsToSend)
        head2 = toEightBytes(lastPacketSize)
        head3 = toEightBytes(SYN)
        head4 = toEightBytes(0)   # 0 for now. This will be replaced by ACK (1 + the 'x' from the counterparty)
        head5 = toEightBytes(314159)
        message = head0+head1+head2+head3+head4+head5
        # eight_bytes_ = message.to_bytes(8, byteorder='big', signed = True)
        if verbose: print(message)
        if verbose: print('reliableSockets.py, sendReliablyBinary line 67: sending initial SYN packet as: ', np.array([0, numPacketsToSend, lastPacketSize, SYN, 0, 314159]),' at time ',int(round(time.time() * 1000)), ' to conn ',conn  )
        conn.sendall(message)
        messageSYN = message  # keep this in case need to resend later

        # LISTEN FOR RECEIPT ACK.
        ACKreceived = False
        timestart = int(round(time.time() * 1000))
        timeElapsed = int(round(time.time() * 1000)) - timestart
        while (ACKreceived == False):
            timeElapsed = int(round(time.time() * 1000)) - timestart
            
            if verbose: print('reliableSockets.py line 78: reading from conn ',conn,' at time ', int(round(time.time() * 1000)))

            message = conn.recv(wholePacketSize)
            head0 = int.from_bytes(message[0:8], byteorder='big')
            head1 = int.from_bytes(message[8:16], byteorder='big')
            head2 = int.from_bytes(message[16:24], byteorder='big')
            head3 = int.from_bytes(message[24:32], byteorder='big')
            head4 = int.from_bytes(message[32:40], byteorder='big')
            head5 = int.from_bytes(message[40:48], byteorder='big')
            if verbose: print('reliableSockets.py line 87: received packet ',np.array([head0, head1, head2, head3, head4, head5]),' at time ', int(round(time.time() * 1000)))
            if (head0 == 0) and (head4 == SYN+1) and (head5 == 314159):
                if verbose: print('reliableSockets.py line 89:  head = 0, head4 = SYN+1, head5 = 314159, time ',int(round(time.time() * 1000)))
                if head4 == SYN+1:
                    ACKreceived = True          # IF RECEIVED, initialPacketRecvd = True
                    initialPacketRecvd = True
                    # numPacketsToSend = head1
                    # lastPacketSize = head2
                    # SYN = head3
                    # ACK = head4
                    if verbose: print('reliableSockets.py, sentReliablyBinary line 97. Received ACK packet as: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))
                else:
                    ACKreceived = True          # wrong ACK received, but set as True so we get back to larger loop to resend SYN
                    if verbose: print('reliableSockets.py line 100. Wrong ACK received as: ', np.array([head0, head1, head2, head3, head4, head5]))
                    # conn.sendall(messageSYN)
                    timestartSYN = int(round(time.time() * 1000))
                    timeElapsedSYN = int(round(time.time() * 1000)) - timestartSYN
                    while timeElapsedSYN < 5:  # wait 5 msec before checking again
                        timeElapsedSYN = int(round(time.time() * 1000)) - timestartSYN                        
                    if verbose: print('line 106: resent SYN at time ',int(round(time.time() * 1000)))
        
            if timeElapsed > 2000:
                if verbose: print('reliableSockets.py line 109: timeElapsed > 2000 msec. Time exceeded for ACK. time now is ',int(round(time.time() * 1000)))
                # conn.close()
                break

    ACK = 1000000001   # 1,000,000,001
    if verbose: print('reliableSockets.py, sendReliablyBinary line 114: received ACK that initial packet is received. Beginning message transmit.')

    finalPacketRecvd = False
    packetsSentFlags = np.zeros(numPacketsToSend, dtype=int, order='C')  # index starts at 0, length is numPacketsToSend
    timestartClock0 = int(round(time.time() * 1000))
    while (finalPacketRecvd == False): # THIS IS THE MAIN LOOP FOR SENDING PACKETS
        # define thisPacketNum as the smallest packet number not yet sent
        thisPacketNum = np.argmax(packetsSentFlags <= 0) + 1  # index starts at 1 not 0
        if verbose: print('reliableSockets.py, sendReliablyBinary  line 122, thisPacketNum = ',thisPacketNum)
        head0 = toEightBytes(thisPacketNum)   # start at 1 count up to numPacketsToSend
        head1 = toEightBytes(numPacketsToSend)
        head2 = toEightBytes(lastPacketSize)
        SYN += 1
        head3 = toEightBytes(SYN)
        head4 = toEightBytes(ACK + 1)   #  (1 + the 'x' from the counterparty)
        head5 = toEightBytes(314159)
        message = head0+head1+head2+head3+head4+head5                
        # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
        # print(eight_bytes)    
        if thisPacketNum != numPacketsToSend: 
            # SEND THE NEXT PACKET
            startByte = dataPacketSize * (thisPacketNum - 1)
            endByte = dataPacketSize * thisPacketNum
            if verbose: print('reliableSockets.py, sendReliablyBinary line 137, startByte ',startByte,', endByte ',endByte)
            thisPacket = msg[dataPacketSize * (thisPacketNum - 1) : dataPacketSize * thisPacketNum ]  # each 2000 bytes
        else:  # this is the last packet, so it's shorter
            startByte = dataPacketSize * (thisPacketNum - 1)
            endByte = len(msg)
            if verbose: print('reliableSockets.py, sendReliablyBinary line 142, startByte ',startByte,', endByte ',endByte)
            thisPacket = msg[dataPacketSize * (thisPacketNum - 1) : len(msg)]
        totalPackage = message + thisPacket
        if verbose: print('reliableSockets.py, sendReliablyBinary  line 145: sending packet ',thisPacketNum,' of ',numPacketsToSend,'. ',len(totalPackage),' bytes')
        conn.sendall(totalPackage)  # concatenated binary  
        if packetsSentFlags[thisPacketNum - 1] == -1:  # just fixed a bad packet. Wait a few milliseconds for it to be received before continuing, so that we don't send multiple 'fixes'
            timestart = int(round(time.time() * 1000))
            timeElapsed = int(round(time.time() * 1000)) - timestart
            while timeElapsed < 5:  # wait 5 msec for recipient to update whether it received the packet or whether it still needs resending
                timeElapsed = int(round(time.time() * 1000)) - timestart                
        packetsSentFlags[thisPacketNum - 1] = 1  # mark this packet number as SENT
        if verbose: print('reliableSockets.py line 153   packetsSentFlags = ', packetsSentFlags)

        # LISTEN FOR RECEIPT of final packet or error about missing packets.
        # IF FINAL RECEIVED, finalPacketRecvd = True
        # IF ERROR, resend the missing packets
        timestart = int(round(time.time() * 1000))
        timeElapsed = int(round(time.time() * 1000)) - timestart
        if verbose: print('reliableSockets.py line 160   starting timestart timeElapsed while loop at time ', timestart)
        while timeElapsed < 2:  # wait 2 msec to listen for recipient response
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    if verbose: print('reading from conn')
                    message = sock.recv(wholePacketSize) 
                    head0 = int.from_bytes(message[0:8], byteorder='big')
                    head1 = int.from_bytes(message[8:16], byteorder='big')
                    head2 = int.from_bytes(message[16:24], byteorder='big')
                    head3 = int.from_bytes(message[24:32], byteorder='big')
                    head4 = int.from_bytes(message[32:40], byteorder='big')
                    head5 = int.from_bytes(message[40:48], byteorder='big')
                    if verbose: print('received ',np.array([head0, head1, head2, head3, head4, head5]))
                    if (head3 == 314159) & (head4 == 314159) & (head5 == 314159): # this is a RESEND request
                        requestedPacketNum = head0
                        packetsSentFlags[requestedPacketNum - 1] = -1   # change this packet number to BAD, RESEND
                        if verbose: print('reliableSockets.py line 177   Received RESEND request for packetNum ', requestedPacketNum)
                        if verbose: print('reliableSockets.py line 178   packetsSentFlags = ', packetsSentFlags)                
                    if (head0 == 72057594037927935) and (head3 == 0) and (head4 == 0): # this indicates DONE, full message received
                        if verbose: print('reliableSockets.py, sendReliablyBinary  line 180: confirming receipt of RECV message that full message has been received. End sendReliablyBinary.')
                        finalPacketRecvd = True
                        emptySocket(conn)  # empty the socket before breaking
                        break
            timeElapsed = int(round(time.time() * 1000)) - timestart
            # print('timeElapsed = ',timeElapsed)
        if verbose: print('finished timestart timeElapsed while loop')
        timeElapsedClock0 = int(round(time.time() * 1000)) - timestartClock0
        if timeElapsedClock0 > 15000:
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            if verbose: print('reliableSockets.py, sendReliablyBinary line 189: WARNING WARNING WARNING timeElapsedClock0 exceeded 15 seconds. Breaking')
            break


def recvReliablyBinary2(conn, data, verbose = False):
    verbose = True

    import time
    import copy
    import numpy as np
    import random
    import select
    # lastX = -1  # the last X received from the sender
    headerReceived = False
    packetSize = 1048
    
    message = data
    head0 = int.from_bytes(message[0:8], byteorder='big')
    head1 = int.from_bytes(message[8:16], byteorder='big')
    head2 = int.from_bytes(message[16:24], byteorder='big')
    head3 = int.from_bytes(message[24:32], byteorder='big')
    head4 = int.from_bytes(message[32:40], byteorder='big')
    head5 = int.from_bytes(message[40:48], byteorder='big')
    if verbose: print('reliableSockets.py, recvReliablyBinary2 line 222: Received: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))
    if (head0 == 0) & (head5 == 314159):
        if verbose: print('reliableSockets.py, recvReliablyBinary2 line 224: Confirmed SYN: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))
    else:
        while (headerReceived == False):  # THIS IS THE LOOP FOR RECEIVING THE INITIAL SYN PACKET
            # message = conn.recv(packetSize)
            if verbose: print('reliableSockets.py, line 228. head0 ~= 0 or head5 ~= 314159. Incorrect SYN received. Trying another read at time ',int(round(time.time() * 1000)),' Don\'t worry this is expected.')    
            message = conn.recv(packetSize)
            head0 = int.from_bytes(message[0:8], byteorder='big')
            head1 = int.from_bytes(message[8:16], byteorder='big')
            head2 = int.from_bytes(message[16:24], byteorder='big')
            head3 = int.from_bytes(message[24:32], byteorder='big')
            head4 = int.from_bytes(message[32:40], byteorder='big')
            head5 = int.from_bytes(message[40:48], byteorder='big')
            if verbose: print('reliableSockets.py, recvReliablyBinary2 line 236: Received: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))
            if (head0 == 0) and (head1 == 0) and (head2 == 0) and (head3 == 0) and (head4 == 0) and (head5 == 0):
                print('reliableSockets.py line 238. Received [0 0 0 0 0 0]. Game Over! Press Ctrl-C to exit.')
                conn.close
                GameOver = True

                head0 = toEightBytes(0)   # Game Over signal = [0,0,0,0,0,0]
                head1 = toEightBytes(0)
                head2 = toEightBytes(0)
                head3 = toEightBytes(0)
                head4 = toEightBytes(0)
                head5 = toEightBytes(0)
                message = head0+head1+head2+head3+head4+head5    
        
                # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
                if verbose: print('reliableSockets.py, recvReliablyBinary line 253: Sending GAME OVER Signal as 8-byte formatted: ', np.array([0, 0, 0, 0, 0, 0]))
                # print(eight_bytes)        
                conn.sendall(message)  #  [-1, 73, 736, 0, 0, 314159]

                if verbose: print('reliableSockets.py, recvReliablyBinary line 257: Sent GAME OVER Signal as 8-byte formatted: ', np.array([0, 0, 0, 0, 0, 0]))
                # emptySocket(conn)
                
                return message  #  pickle is expecting the full message as bytes not bytearray

            if (head0 == 0) & (head5 == 314159):
                if verbose: print('reliableSockets.py, recvReliablyBinary2 line 242: Confirmed SYN: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)))
                headerReceived = True            
            else:
                timestart = int(round(time.time() * 1000))
                timeElapsed = int(round(time.time() * 1000)) - timestart
                while timeElapsed < 5:
                    timeElapsed = int(round(time.time() * 1000)) - timestart
    
    numPacketsToSend = head1
    lastPacketSize = head2
    SYN = head3
    ACK = head4
            
    # send ACK Ready signal
    head0 = toEightBytes(0)   # 0 indicates that this is the initial packet for SYN
    head1 = toEightBytes(numPacketsToSend)
    if verbose: print('reliableSockets.py recvReliablyBinary2  line 258:  lastPacketSize = ',lastPacketSize)
    head2 = toEightBytes(lastPacketSize)
    SeqNum = random.randrange(3000000000,4000000000)
    head3 = toEightBytes(SeqNum)
    head4 = toEightBytes(SYN + 1)   
    head5 = toEightBytes(314159)
    message = head0+head1+head2+head3+head4+head5
    # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
    if verbose: print('reliableSockets.py, recvReliablyBinary line 266: Sending ACK Ready Signal as 8-byte formatted version of: ', np.array([0, numPacketsToSend, lastPacketSize, SeqNum, SYN + 1, 314159]),' at time ',int(round(time.time() * 1000)) )
    # print('reliableSockets.py, recvReliablyBinary line 252: Sending ACK Ready Signal as: ', message)
    conn.sendall(message)
    messageACK = message

    expectedMsgLength = numPacketsToSend*(packetSize - 48) + lastPacketSize - 48
    # messageContainer = np.zeros(expectedMsgLength, dtype=int, order = 'C')  # ACTUALLY, I DON'T KNOW WHAT DTYPE DILL/PICKLE USES, and what ORDER.
    messageContainer = bytearray(expectedMsgLength)
    packetsReceivedFlags = np.zeros(numPacketsToSend, dtype=int, order='C')
    finalPacketReceived = False

    # wait a few msec before checking
    timestartACK = int(round(time.time() * 1000))    
    timeElapsedACK = int(round(time.time() * 1000)) - timestartACK
    while (timeElapsedACK < 5):  # pausing for initial ACK packet
        timeElapsedACK = int(round(time.time() * 1000)) - timestartACK

    timestartResendRequest = int(round(time.time() * 1000))    # initialize this value here... will update later after RESEND request
    timestart = int(round(time.time() * 1000))    
    timeElapsed = int(round(time.time() * 1000)) - timestart
    
    # MAYBE THE ACK DIDN'T GET THROUGH?
    # while the received packet num is 0, repeat sending ACK...
    
    
    while (finalPacketReceived == False) & (timeElapsed < 5000): # THIS IS THE MAIN LOOP FOR RECEIVING PACKETS. Allow max wait of 5000 msecs
        timeElapsed = int(round(time.time() * 1000)) - timestart
        message = conn.recv(packetSize)
        head0 = int.from_bytes(message[0:8], byteorder='big')  # packet number
        head1 = int.from_bytes(message[8:16], byteorder='big') # number of packets to send
        head2 = int.from_bytes(message[16:24], byteorder='big') # last packet size
        head3 = int.from_bytes(message[24:32], byteorder='big')
        head4 = int.from_bytes(message[32:40], byteorder='big')
        head5 = int.from_bytes(message[40:48], byteorder='big')
        thisPacketNum = head0
        numPacketsToSend = head1
        lastPacketSize = head2
        SYN = head3
        ACK = head4
        if verbose: print('reliableSockets.py, recvReliablyBinary line 305: Received: ', np.array([head0, head1, head2, head3, head4, head5]),' at time ',int(round(time.time() * 1000)) )
        if (thisPacketNum == 0):
            # ACK probably not received. Send again, then wait a few msec.
            if verbose: print('reliableSockets.py line 308. Received packet 0, ACK not received? Resending ACK at time ',int(round(time.time() * 1000)) )
            conn.sendall(messageACK)
            # wait a few msec before checking again
            timestartACK = int(round(time.time() * 1000))    
            timeElapsedACK = int(round(time.time() * 1000)) - timestartACK
            while (timeElapsedACK < 5):  # pausing for initial ACK packet
                timeElapsedACK = int(round(time.time() * 1000)) - timestartACK

        if (thisPacketNum > 0) and (head5 == 314159):
              
            # qcPassed = False
            # basic quality check
            if (thisPacketNum > 0) & (thisPacketNum < numPacketsToSend):  # this is any packet except the last packet of the series
                if len(message) == packetSize:
                    # qcPassed = True
                    dataPacket = message[48:packetSize]
                    startIdx = (thisPacketNum - 1) * (packetSize - 48)
                    endIdx = (thisPacketNum * (packetSize - 48))
                    if verbose: print('reliableSockets.py, receiveReliablyBinary2 line 326:  startIdx ',startIdx,', endIdx ',endIdx) # write this dataPacket to the appropriate place of messageContainer
                    if packetsReceivedFlags[thisPacketNum - 1] < 1:
                        messageContainer[startIdx:endIdx] = bytearray(dataPacket)  # COPYING THE PACKET TO THE RIGHT PLACE in memory
                        # and update the flags of which packets have been received.                
                        packetsReceivedFlags[thisPacketNum - 1] = 1   # mark it as a finished packet.   THIS IS SCENARIO 1
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 331: marked packet ',thisPacketNum,' as good')         
                        timestartResendRequest = int(round(time.time() * 1000))    # just received a good packet. Extend the wait time before any attempt to request RESEND
                    else:  # we already have a good copy of this packet. No need to overwrite or update timestartResendRequest
                        if verbose: print('We already have a good copy of this packet. No need to update messageContainer or timestartResendRequest clock.')
                else:
                    if verbose: print('reliableSockets.py, recvReliablyBinary2, line 336:  len(message) = ',len(message),', expected 2048')
                    packetsReceivedFlags[thisPacketNum - 1] = -1   # mark it as a bad packet that needs resending.   THIS IS SCENARIO 2
                    if verbose: print('reliableSockets.py, recvReliablyBinary line 338: marked packet ',thisPacketNum,' as bad')                    
            if (thisPacketNum == numPacketsToSend):  # this is the last packet of the series
                if len(message) == lastPacketSize:
                    # qcPassed = True
                    startIdx = (thisPacketNum - 1) * (packetSize - 48)
                    endIdx = startIdx + lastPacketSize - 48
                    dataPacket = message[48:lastPacketSize]
                    # messageContainer[startIdx:endIdx] = copy.deepcopy(dataPacket) # COPYING THE PACKET TO THE RIGHT PLACE in memory
                    if packetsReceivedFlags[thisPacketNum - 1] < 1:
                        messageContainer[startIdx:endIdx] = bytearray(dataPacket) # COPYING THE PACKET TO THE RIGHT PLACE in memory
                        packetsReceivedFlags[thisPacketNum - 1] = 1   # mark it as a finished packet.   THIS IS SCENARIO 3                    
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 349: marked packet ',thisPacketNum,' as good')                    
                        timestartResendRequest = int(round(time.time() * 1000))    # just received a good packet. Extend the wait time before any attempt to request RESEND
                    else:
                        if verbose: print('We already have a good copy of this packet. No need to update messageContainer or timestartResendRequest clock.')                        
                else:
                    if verbose: print('len(message) = ',len(message),', expected length is ', lastPacketSize)
                    packetsReceivedFlags[thisPacketNum - 1] = -1   # mark it as a bad packet.   THIS IS SCENARIO 4
                    if verbose: print('reliableSockets.py, recvReliablyBinary line 356: marked packet ',thisPacketNum,' as bad')                    
            # CHECK IF ALL PACKETS ARE RECEIVED
            if verbose: print('reliableSockets.py, recvReliablyBinary line 358, packetsReceivedFlags = ',packetsReceivedFlags)
            if min(packetsReceivedFlags) == 1:   # THIS IS SCENARIO 0
                if verbose: print('reliableSockets.py, recvReliablyBinary line 360: All Packets Received')
                head0 = toEightBytes(72057594037927935)   # '72057594037927935' = '-1' = b'\xff\xff\xff\xff\xff\xff\xff\xff'
                head1 = toEightBytes(numPacketsToSend)
                head2 = toEightBytes(lastPacketSize)
                head3 = toEightBytes(0)
                head4 = toEightBytes(0)
                head5 = toEightBytes(314159)
                message = head0+head1+head2+head3+head4+head5    
        
                # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
                if verbose: print('reliableSockets.py, recvReliablyBinary line 370: Sending ALL PACKETS RECEIVED Signal as 8-byte formatted: ', np.array([head0, head1, head2, head3, head4, head5]))
                # print(eight_bytes)        
                conn.sendall(message)  #  [-1, 73, 736, 0, 0, 314159]

                if verbose: print('reliableSockets.py, recvReliablyBinary line 374: Sent ALL PACKETS RECEIVED Signal as 8-byte formatted: ', np.array([head0, head1, head2, head3, head4, head5]))
                emptySocket(conn)
                
                return bytes(messageContainer)  #  pickle is expecting the full message as bytes not bytearray
            
            # Scenario 0:  packetsReceivedFlags = [1 1 1 1 1 1 1 1]     confirmed that all packets received are good
            # Scenario 1:  packetsReceivedFlags = [1 1 1 1 0 0 0 0]    and we just finished receiving packet 4 of 8 and updated the flag to 1. thisPacketNum = 4. Just wait!
            # Scenario 2:  packetsReceivedFlags = [1 1 1 -1 0 0 0 0]    and we just received bad packet 4 of 8 and updated the flag to -1. thisPacketNum = 4.  need to request RESEND packet 4
            # Scenario 3:  packetsReceivedFlags = [1 1 1 1 1 1 -1 1]    and we just finished receiving packet 8 of 8 and updated the flag to 1. thisPacketNum = 8.  need to wait, because request for RESEND of packet 7 should already have been made
            # Scenario 4:  packetsReceivedFlags = [1 1 1 1 1 1 -1 -1]    and we just received bad packet 8 of 8 and updated the flag to -1. thisPacketNum = 8.  need to request RESEND packet 8
            # Scenario 5:  packetsReceivedFlags = [1 0 1 0 0 0 0 0]     missing packet 2 of 8. thisPacketNum = 3.   need to request RESEND packet 2
            # Scenario 6:  packetsReceivedFlags = [1 1 1 1 1 1 1 0]     just received packet 7. packet 8 of 8 not yet received. thisPacketNum = 7. Just wait!
            # Scenario 7:  packetsReceivedFlags = [1 1 1 1 1 1 1 -1]     received bad packet 8 of 8. thisPacketNum = 8     need to request RESEND packet 8
            # Scenario 8:  packetsReceivedFlags = [1 1 1 1 1 1 -1 1]     received bad packet 7 of 8. thisPacketNum = 7     need to request RESEND packet 7
            
            if (packetsReceivedFlags < 1).any():  # if any packets are bad or not yet received, i.e. Scenarios 1-8
                # check if the current packet number exceeds the smallest missing packet number
                smallestMissingPacketNum = np.argmax(packetsReceivedFlags <= 0) + 1
                if verbose: print('reliableSockets.py, recvReliablyBinary2, line 392:  smallestMissingPacketNum is ',smallestMissingPacketNum)
                if verbose: print('thisPacketNum = ',thisPacketNum)
                if (smallestMissingPacketNum <= thisPacketNum): # SCENARIOS 2-5 7, 8
                    if packetsReceivedFlags[smallestMissingPacketNum - 1] == -1:  # Flag is -1. Request RESEND
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 396: requesting resend of packet number ',smallestMissingPacketNum)
                        # request a resend
                        head0 = toEightBytes(smallestMissingPacketNum)   # the missing packet number being requested
                        head1 = toEightBytes(numPacketsToSend)
                        head2 = toEightBytes(lastPacketSize)
                        head3 = toEightBytes(314159)
                        head4 = toEightBytes(314159)
                        head5 = toEightBytes(314159)
                        message = head0+head1+head2+head3+head4+head5    
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 405: Requesting RESEND: ', np.array([head0, head1, head2, head3, head4, head5]))
                
                        # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
                        # print(eight_bytes)        
                        conn.sendall(message)
                        packetsReceivedFlags[smallestMissingPacketNum - 1] = 0   # RESEND requested. Update flag to 0
                        timestartResendRequest = int(round(time.time() * 1000))    
                        
                    if (packetsReceivedFlags[smallestMissingPacketNum - 1] == 0) and (int(round(time.time() * 1000)) - timestartResendRequest) > 50:
                        if verbose: print('reliableSockets.py line 414:  It has been 50 msec since last request but still not updated. Change flag from 0 to -1 to request RESEND')
                        packetsReceivedFlags[smallestMissingPacketNum - 1] = -1

                if (smallestMissingPacketNum > thisPacketNum): # SCENARIOS 1, 6
                    if (int(round(time.time() * 1000)) - timestartResendRequest) > 50:
                        if verbose: print('reliableSockets.py line 409: It has been 50 msec since last request but still not updated. Changing packetsReceivedFlags[smallestMissingPacketNum - 1] from 0 to -1 to request RESEND')
                        packetsReceivedFlags[smallestMissingPacketNum - 1] = -1
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 421: requesting resend of packet number ',smallestMissingPacketNum)
                        # request a resend
                        head0 = toEightBytes(smallestMissingPacketNum)   # the missing packet number being requested
                        head1 = toEightBytes(numPacketsToSend)
                        head2 = toEightBytes(lastPacketSize)
                        head3 = toEightBytes(314159)
                        head4 = toEightBytes(314159)
                        head5 = toEightBytes(314159)
                        message = head0+head1+head2+head3+head4+head5    
                        if verbose: print('reliableSockets.py, recvReliablyBinary line 430: Requesting RESEND: ', np.array([head0, head1, head2, head3, head4, head5]))
                
                        # eight_bytes = message.to_bytes(8, byteorder='big', signed = True)
                        # print(eight_bytes)        
                        conn.sendall(message)
                        packetsReceivedFlags[smallestMissingPacketNum - 1] = 0   # RESEND requested. Update flag to 0
                        timestartResendRequest = int(round(time.time() * 1000))    

    if (finalPacketReceived == False) and (timeElapsed >= 15000):
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        if verbose: print('reliableSockets.py line 439:  WARNING WARNING WARNING Fifteen seconds have elapsed but finalPacketReceived = False. Breaking!')
        return
                    
def emptySocket(conn, verbose = False):
    verbose = True
    import select
    # empty this socket before continuing
    if verbose: print('reliableSockets.py recvReliablyBinary2 line 455:  emptying socket')
    timestartClock1 = int(round(time.time() * 1000))    
    timeElapsedClock1 = int(round(time.time() * 1000)) - timestartClock1
    while timeElapsedClock1 < 1:
        timeElapsedClock1 = int(round(time.time() * 1000)) - timestartClock1
        # print('reliableSockets.py line 320  timeElapsedClock1: ',timeElapsedClock1)
        try:
            readable, writable, errored = select.select([conn], [], [],0)
            for sock in readable:
                if sock is conn:
                    junk = conn.recv(1024)
        except:
            break
    if verbose: print('socket emptied')                
                    
