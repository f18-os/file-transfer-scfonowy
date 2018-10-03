#! /usr/bin/env python3
import sys
sys.path.append("../lib")       # for params
import os, re, socket, params

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


from fileTransferSocket import fileReceive

accepting_connections = True
while accepting_connections:
    if debug: print("awaiting new connection")
    sock, addr = lsock.accept() # TODO: fork on new connection
    print("connection rec'd from", addr)
    fork_code = os.fork()

    if fork_code == 0: # in child
        accepting_connections = False # stop accepting new connections on this thread
        while True:
            # start receipt session
            try:
                if debug: print("awaiting file")
                fileReceive(sock, receiptDirectory, debug)
            except Exception as e:
                print("connection closed: " + str(e))
                quit()
    else: # in parent
        continue