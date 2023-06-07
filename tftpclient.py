#!/usr/bin/python3
import socket
import sys
import os
import signal
import errno


def shutdownServer(signum, frame):
    print("server shutdown ...")
    sys.exit(0)


def collectZombie(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
        except:
            break


def getFile(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "<HTML><BODY><H1>File not found</H1></BODY></HTML>"


def doHTTPService(sock):
    try:
        reqMessage = sock.recv(RECV_BUFF)
    except ConnectionResetError as e:
        sock.close()
        return
    if reqMessage:
        msgString = bytes.decode(reqMessage)
        print(msgString)
        lines = msgString.split('\r\n')
        reqLine = lines[0]
        fields = reqLine.split(' ')
        method = fields[0]
        reqURL = fields[1]
        ver = fields[2]
        print('requested URL: {}'.format(reqURL))
    else:
        sock.close()
        return
    statusLine = 'HTTP/1.1 200 OK\r\n'
    headerLine1 = 'Server: vshttpd 0.1\r\n'
    headerLine2 = 'Connection: close\r\n\r\n'

    responseBody = ""
    if reqURL == "/":
        responseBody = '''<HTML><BODY><H1><a href="/linked.html"> Go to linked.html document!</a></H1></BODY></HTML>'''

    else:
        responseBody = getFile(reqURL[1:])

    sock.sendall(statusLine.encode())
    sock.sendall(headerLine1.encode())
    sock.sendall(headerLine2.encode())
    sock.sendall(responseBody.encode())
    sock.close()


HOST_IP = '203.250.133.88'
PORT = 18909
BACKLOG = 5
RECV_BUFF = 10000
signal.signal(signal.SIGINT, shutdownServer)
signal.signal(signal.SIGCHLD, collectZombie)

try:
    connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    print("failed to create a socket")
    sys.exit(1)
try:
    connSock.bind((HOST_IP, PORT))
except Exception as e:
    print("failed to acquire sockets for port {}".format(PORT))
    sys.exit(1)
print("server running on port {}".format(PORT))
print("press Ctrl+C (or $kill -2 pid) to shutdown the server")
connSock.listen(BACKLOG)

while True:
    print("waiting a new connection...")
    try:
        dataSock, addr = connSock.accept()
        print("got a connection request from: {}".format(addr))
    except IOError as e:
        code, msg = e.args
        if code == errno.EINTR:
            continue
        else:
            raise
    pid = os.fork()
    if pid == 0:
        doHTTPService(dataSock)
        sys.exit(0)
    dataSock.close()