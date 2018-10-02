import re
from enum import Enum

# enum for what state we're in when receiving a file
class FileReceiveState(Enum):
    NAME_LENGTH = 1
    NAME_PAYLOAD = 2
    FILE_LENGTH = 3
    FILE_PAYLOAD = 4
    COMPLETE = 5
    ERROR = 4

# enum for what state we're in when receiving a message
class MessageReceiveState(Enum):
    LENGTH = 1
    PAYLOAD = 2
    COMPLETE = 3
    ERROR = 4

def framedSend(sock, payload, debug=0):
    if debug: print("framedSend: sending %d byte message" % len(payload))
    msg = str(len(payload)).encode() + b':' + payload
    while len(msg):
        nsent = sock.send(msg)
        msg = msg[nsent:]
     
rbuf = b""                      # static receive buffer

def framedReceive(sock, debug=0):
    global rbuf
    state = MessageReceiveState.LENGTH
    payload = None
    msgLength = -1

    while state != MessageReceiveState.COMPLETE and state != MessageReceiveState.ERROR: # check for terminal states
        r = sock.recv(100) # read part of message and update buffer
        rbuf += r

        if (state == MessageReceiveState.LENGTH): # parse length
            match = re.match(b'([^:]+):(.*)', rbuf) # look for colon
            if match:
                lengthStr, rbuf = match.groups()

                try: 
                    msgLength = int(lengthStr)
                    state = MessageReceiveState.PAYLOAD
                except:
                    state = MessageReceiveState.ERROR
                    if len(rbuf):
                        print("badly formed message length:", lengthStr)
        

        if state == MessageReceiveState.PAYLOAD: # check if payload is complete
            if len(rbuf) >= msgLength: # truncate message
                payload = rbuf[0:msgLength]
                rbuf = rbuf[msgLength:]
                state = MessageReceiveState.COMPLETE

        # error/zero length case
        if not r or len(r) == 0:
            state = MessageReceiveState.ERROR
            if len(rbuf) != 0:
                print("FramedReceive: incomplete message. \n  state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))
            payload = None # don't return potentially partial message

        if debug:
            print("FramedReceive: state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))

    return payload

def fileSend(sock, file, debug=0):
    # TODO: get file name & length & send

    # TODO: send file
    return

def fileReceive(sock, debug=0):
    # TODO: receive file name and check if exists (if so, send error)

    # TODO: receive file size and then file, saving to disk
    return