#! /usr/bin/env python3
import sys
sys.path.append("../lib")       # for params
import os, re, socket, params
from fileTransferSocket import fileReceive

### BEGIN PROVIDED CODE BLOCK
switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)
receiptDirectory = "./received_files/" # directory used to store files

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)
### END PROVIDED CODE BLOCK

accepting_connections = True
while accepting_connections: # loop that waits for connections & forks when a client connects
    if debug: print("awaiting new connection")
    sock, addr = lsock.accept() # blocks thread until client connects
    print("connection rec'd from", addr)
    fork_code = os.fork()

    if fork_code == 0: # in child
        accepting_connections = False # stop accepting new connections on this thread
        while True:
            # start file put session
            try:
                if debug: print("awaiting file")
                fileReceive(sock, receiptDirectory, debug)
            except Exception as e: # most likely, client disconnected
                print("connection closed: " + str(e))
                quit()
    else: # in parent
        continue