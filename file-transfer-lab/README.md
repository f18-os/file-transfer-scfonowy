# CS4375 - File Transfer Lab
--
*by super anonymous student, last update October 3rd, 2018*
## Overview
This is a *very* simple file transfer server/client setup. The server accepts client connections and puts all files within the same folder. The client can only send files that are in the same directory as the fileTransferClient.py file. The server is capable of handling multiple connections and transfers at once, but will most likely break if you try to upload two files of the same name and extension at the same time.

The client first sends a framed message (using code provided by Dr. Freudenthal) indicating the file name to the server. The server then responds with either an error code or an acknowledgement to proceed with upload. The client then uploads the entire file using a modified version of the framedSend code that breaks the message into 100 byte chunks. The framedReceive code is used to handle receiving the file, that is then written to disk. The process completes with the server sending either an error or completion acknowledgement.

## Running Instructions
To run the lab, simply download or clone the repository and run the server script using `python3`. For example:

`python3 file-transfer-lab/fileTransferServer.py` or `./file-transfer-lab/fileTransferServer.py`

Then, start any number of clients in a similar fashion:

`python3 file-transfer-lab/fileTransferClient.py` or `./file-transfer-lab/fileTransferClient.py`

You may also wish to use the stammer proxy provided. To do so, simply run the proxy and change the port that the client connects to, either by editing the script or using the server flag.

## References
Much of the code for sending and receiving messages was provided by Dr. Freudenthal.

The Python documentation describing sockets was consulted, though I'm not sure if I used much of it. (https://docs.python.org/2/library/socket.html)

I also had to look up how to define Enums in Python, since I wanted to use those for server states.

I also referenced this StackOverflow question that covered reading and writing a file by its bytes rather than lines (https://stackoverflow.com/questions/6787233/python-how-to-read-bytes-from-file-and-save-it).