#!/usr/bin/env python
import socket,sys,multiprocessing


IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
print TCP_PORT,"port"
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
port_listen=5100
def read_thread(q):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((IP, port_listen))
        s.listen(5)

        while 1:
                        conn, addr = s.accept()
                        data = conn.recv(BUFFER_SIZE)
                        if not data: break
                        #conn.send(data) #echo
                        q.put(data)
                        print "received",data
                        data=0 #reset the buffer        
                        #conn.close() 
queue = multiprocessing.Queue()
p = multiprocessing.Process(target=read_thread, args=(queue,))
p.start()
#p.join()

while 1:
        data=raw_input("Enter Value")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, TCP_PORT))
        s.send(data)
        #data = s.recv(BUFFER_SIZE) #echo
        s.close()

print "received data:", data
