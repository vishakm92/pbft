#!/usr/bin/env python

import socket,sys


TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
print TCP_PORT,"port"
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while 1:
	s.send(raw_input("Enter Value"))
	data = s.recv(BUFFER_SIZE)

s.close()

print "received data:", data