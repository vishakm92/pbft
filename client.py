#!/usr/bin/env python
import socket,sys,multiprocessing,pylibmodbus

IP = '127.0.0.1'
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
port_listen_replica=5100
port_listen_master=5101
seq_process=0
def toHex(s):
        lst = []
        for ch in s:
                hv = hex(ord(ch)).replace('0x', '')
                if len(hv) == 1:
                        hv = '0'+hv
                lst.append(hv) 
        return reduce(lambda x,y:x+y, lst)

def send_to_slave(q,r):
        while 1:        
                s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_local.connect((IP, 502))
                s_local.send(q.get())
                data=s_local.recv(BUFFER_SIZE)
                r.put(data)
                print "response obtained",toHex(data)

def listen_replica(q,r):
        global port_listen_replica,seq_process
        s_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_replica.bind((IP, port_listen_replica))
        s_replica.listen(5)
        while 1:
                conn, addr = s_replica.accept()
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                #conn.send(data) #echo
                modbus_response=data.split(",")
                print "response",toHex(modbus_response[0]),modbus_response[1]
                #print "these should be same",toHex(response),toHex(r.get()),toHex(r.get()),toHex(r.get()) 
                if seq_process < int(modbus_response[1]):
                        print "sending resposne",toHex(modbus_response[0])
                        r.put(modbus_response[0])
                        seq_process=seq_process+1
                #print "received response --",toHex(data)
                data=0 #reset the buffer        
                #conn.send()
                #conn.close() 


def listen_master(q,r):
        global port_listen_master,seq_process
        s_master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_master.bind((IP, 5101))
        s_master.listen(5)
        while 1:
                conn, addr = s_master.accept()
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                #conn.send(data) #echo
                q.put(data)
                #print "received query",toHex(data)
		#query=toHex(data)
		#print "register is",query[16:20]
                data=0 #reset the buffer      
		#print "these should be same",toHex(response),toHex(r.get()),toHex(r.get()),toHex(r.get()) 
		conn.send(r.get())
		conn.close() 

def send_leader_server(q,r):
        TCP_PORT = 5000
        while 1:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((IP, TCP_PORT))
                s.send(q.get())
                print "sent to the server leader"
                # data = s.recv(BUFFER_SIZE) #echo
                s.close()               

query = multiprocessing.Queue()
response = multiprocessing.Queue()

p = multiprocessing.Process(target=listen_master, args=(query,response))
p.start()

p1 = multiprocessing.Process(target=listen_replica, args=(query,response))
p1.start()

p2 = multiprocessing.Process(target=send_leader_server, args=(query,response))
p2.start()

p3 = multiprocessing.Process(target=send_to_slave, args=(query,response))
#p3.start()

