#! /usr/bin/env python3

### BEGIN PROVIDED CODE BLOCK
# Echo client program
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
from fileTransferSocket import fileSend


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)
### END PROVIDED CODE BLOCK

try: # loop that prompts for input and puts the passed file on the server
    command = str(input("Enter 'put <filename>' or 'quit' to exit: \n"))
    while command != "quit":
        commands = command.split() # get filename
        if len(commands) != 2 or commands[0] != "put":
            print("Invalid command.")
        else:
            filename = commands[1]
            fileSend(s, filename, debug) # send to server
        command = str(input("Enter 'put <filename>' or 'quit' to exit: \n"))
except Exception as e: # connection w/ server broke somehow
    print("Session closed, error communicating with server: " + str(e))
