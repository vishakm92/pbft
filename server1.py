import socket
import os,time


def child():
	for i in range(0,10):
		print 'A new child ',  os.getpid()
		time.sleep(1)
	os._exit(0) 


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


newpid = os.fork()
if newpid == 0:
	child()

while 1:
	conn, addr = s.accept()
	data = conn.recv(BUFFER_SIZE)
	if not data: continue
	print "received data:", data
	conn.send(data)  # echo
conn.close()
