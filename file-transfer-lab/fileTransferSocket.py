import re, os, time
from enum import Enum

# enum for what state we're in when receiving a file
class FileReceiveState(Enum):
    NAME = 1
    FILE = 2
    COMPLETE = 3
    ERROR = 4

# enum for what state we're in when receiving a message
class MessageReceiveState(Enum):
    LENGTH = 1
    PAYLOAD = 2
    COMPLETE = 3
    ERROR = 4

### BEGIN CODE CITED FROM PROVIDED CODE
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
            match = re.match(b'([^:]+):(.*)', rbuf, re.DOTALL | re.MULTILINE) # look for colon
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
            payload = None # don't return partial message

        if debug:
            print("FramedReceive: state=%s, length=%d, rbuf=%s" % (state, msgLength, rbuf))

    return payload
### END CODE CITED FROM PROVIDED CODE

# function that sends a file 100 bytes at a time. sampled from framedSend
def fileSend(sock, filename, debug=0):
    if not os.path.isfile(filename):
        print("FileSend: file does not exist.")
        return
    
    sendingFile = open(filename, "rb")
    # send name
    framedSend(sock, filename.encode(), debug)

    # get name acknowledgement
    if FileReceiveState(int(framedReceive(sock, debug).decode())) == FileReceiveState.ERROR:
        print("FileSend: unable to send file, file may exist.")
        return

    # get file length
    fileLength = os.path.getsize(filename)
    if debug: print("file size: " + str(fileLength))
    
    fileBytes = sendingFile.read(100) # construct header w/ initial send
    headerMsg = (str(fileLength) + ":").encode() + fileBytes
    if debug: print("sending header: " + str(headerMsg))
    sock.send(headerMsg)

    # send rest of the file 100 bytes at a time
    fileBytes = sendingFile.read(100)
    while len(fileBytes) > 0:
        if debug: print("sending next 100 bytes...")
        sock.send(fileBytes)
        fileBytes = sendingFile.read(100)

    # check status
    if FileReceiveState(int(framedReceive(sock, debug).decode())) == FileReceiveState.ERROR:
        print("FileSend: error sending file, try again.")

    
# function that receives a file over the network. makes use of framedReceive.
def fileReceive(sock, directory, debug=0):
    state = FileReceiveState.NAME
    filename = None

    while state != FileReceiveState.COMPLETE and state != FileReceiveState.ERROR:
        if state == FileReceiveState.NAME: # get filename
            filename = framedReceive(sock, debug)
            if filename == None:
                state = FileReceiveState.ERROR
                print("FileReceive: unable to read filename. \n")
            elif os.path.isfile(directory + str(filename.decode())):
                state = FileReceiveState.ERROR
                print("FileReceive: file already exists. \n")
            else:
                filename = str(filename.decode())
                state = FileReceiveState.FILE
                if debug: print("FileReceive: ready to receive file %s" % (filename))
        
        elif state == FileReceiveState.FILE: # get file
            fileBytes = framedReceive(sock, debug)
            if fileBytes == None:
                state = FileReceiveState.ERROR
                print("FileReceive: error receiving file. \n")
            else:
                try:
                    outputFile = open(directory + filename, "wb")
                    outputFile.write(fileBytes)
                    outputFile.close()
                    state = FileReceiveState.COMPLETE
                except Exception as e:
                    state = FileReceiveState.ERROR
                    print("FileReceive: error writing file: " + str(e))

        framedSend(sock, str(state.value).encode(), debug) # indicate error/ready to continue
        