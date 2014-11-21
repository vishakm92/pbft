import socket
import os,time,Queue,exceptions
IP = '127.0.0.1'
PORT_C = 5010
BUFFER_SIZE = 20  # Normally 1024, but we want fast response


PORT_S1=5002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT_C))
s.listen(1)
r, w = os.pipe() 
r,w=os.fdopen(r,'r',0), os.fdopen(w,'w',0)
conn, addr = s.accept()

def child():
	while 1:
		try:
			data = conn.recv(BUFFER_SIZE)
			if not data: continue
			conn.send(data) #echo
			print "data",data
			
			r.close()
			#"Child pipe writing"
			print >>w,"%s" % data
			w.flush()
			#"Child pipe closing"
		except KeyboardInterrupt:
			conn.close()


newpid = os.fork()
if newpid == 0:
	child()

while 1:
	time.sleep(1)
	w.close()
	while 1:
		try:
			data=r.readline()
			if not data: break
			q.put(data.strip())
		except KeyboardInterrupt:
			conn.close()
