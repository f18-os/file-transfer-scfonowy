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

class ReceiveState(Enum):
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
    state = ReceiveState.LENGTH
    payload = None
    msgLength = -1

    while state != ReceiveState.COMPLETE and state != ReceiveState.ERROR: # check for terminal states
        if (state == ReceiveState.LENGTH):
            match = re.match(b'([^:]+):(.*)', rbuf) # look for colon
            if match:
                lengthStr, rbuf = match.groups()
                try: 
                    msgLength = int(lengthStr)
                    state = ReceiveState.PAYLOAD
                except:
                    if len(rbuf):
                        print("badly formed message length:", lengthStr)
                        state = ReceiveState.ERROR

        if state == ReceiveState.PAYLOAD:
            if len(rbuf) >= msgLength:
                payload = rbuf[0:msgLength]
                rbuf = rbuf[msgLength:]
                state = ReceiveState.COMPLETE
        r = sock.recv(100)
        rbuf += r

        # error/zero length cases
        if len(r) == 0:
            if len(rbuf) != 0:
                print("FramedReceive: incomplete message. \n  state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))
            payload = None # don't return potentially partial message
            state = ReceiveState.ERROR

        if debug:
            print("FramedReceive: state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))

    return payload # 

def fileSend(sock, file, debug=0):
    # TODO: get file name & length & send

    # TODO: send file
    return

def fileReceive(sock, debug=0):
    # TODO: receive file name and check if exists (if so, send error)

    # TODO: receive file size and then file, saving to disk
    return