from socket import *

 

HOST = '<broadcast>'

PORT = 8880

BUFSIZE = 1024

 

ADDR = (HOST, PORT)

 

udpCliSock = socket(AF_INET, SOCK_DGRAM)

udpCliSock.bind(('', 0))

udpCliSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while True:

    data = input('>')

    if not data:

        break

    print ("sending -> %s"%data)

    udpCliSock.sendto(bytes(data.encode("utf-8")),ADDR)

##    data,ADDR = udpCliSock.recvfrom(BUFSIZE)

##    if not data:

##        break

##    print data

 

udpCliSock.close()