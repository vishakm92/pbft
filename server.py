import socket,multiprocessing,sys
import os,time,Queue,exceptions
IP = '127.0.0.1'
PORT_C = int(sys.argv[2])
print "connecting to port",PORT_C
BUFFER_SIZE = 20  # Normally 1024, but we want fast response


PORT_S1=5002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT_C))
s.listen(1)
conn, addr = s.accept()



def send_preprepare(q):
	TCP_IP = '127.0.0.1'
	TCP_PORT = 5000
	BUFFER_SIZE = 1024
	#send preprepare to all ports
	while 1:
		while not q.empty():
			MESSAGE = q.get()
			for i in range(int(sys.argv[1])):
				PORT = i+5001
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((TCP_IP, PORT))
				s.send("Preprepare, "+MESSAGE)#conconcanate with string, prepare, View number - (port-5000)
				s.close()

def read_thread(q):
	while 1:
		try:
			data = conn.recv(BUFFER_SIZE)
			if not data: continue
			conn.send(data) #echo
			print "data",data
			q.put(data)	
		except KeyboardInterrupt:
			conn.close()


def leader_activity(q):
	while 1:
        	time.sleep(20)
	        while not q.empty():
			print q.get()
			

queue = multiprocessing.Queue()
p = multiprocessing.Process(target=read_thread, args=(queue,))
p.start()

leader = multiprocessing.Process(target=send_preprepare, args=(queue,))
leader.start()

