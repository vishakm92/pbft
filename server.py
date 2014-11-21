#command line argument - 1. number of failures
import socket,multiprocessing,sys
import os,time,Queue,exceptions
IP = '127.0.0.1'
PORT_C = 5000
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
seq_no=0

PORT_S1=5002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT_C))
s.listen(5)



def send_preprepare(q):
	global seq_no
	print "in send preprepare function"
	TCP_IP = '127.0.0.1'
	BUFFER_SIZE = 1024
	while 1:
		#send preprepare to all ports
		MESSAGE = q.get()
		client_port=q.get()

		if not (( MESSAGE.startswith("Prepare")) or ( MESSAGE.startswith("Commit"))):
			print "going to broadcast",MESSAGE
			for i in range(int(sys.argv[1])):
				PORT = i+5001
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((TCP_IP, PORT))
				s.send("Preprepare,"+str(seq_no)+","+MESSAGE)#conconcanate with string, prepare, View number - (port-5000)
				s.close()
			seq_no=seq_no+1	
		else:
			print "Received",MESSAGE

def read_thread(q):
	while 1:
			conn, addr = s.accept()
			data = conn.recv(BUFFER_SIZE)
			if not data: break
			#conn.send(data) #echo
			q.put(data)
			q.put(addr)
			data=0 #reset the buffer	
			#conn.close()
queue = multiprocessing.Queue()
p = multiprocessing.Process(target=read_thread, args=(queue,))
p.start()

leader = multiprocessing.Process(target=send_preprepare, args=(queue,))
leader.start()
leader.join()
p.join()
