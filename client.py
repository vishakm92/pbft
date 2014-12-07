#!/usr/bin/env python
import socket,sys,multiprocessing,pylibmodbus,binascii

IP = '127.0.0.1'
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
port_listen_replica=5100
port_listen_master=5101
seq_process=0
transactionID="0001"
protocolID="0000"
length="0005"
unitID="ff"
functioncode="04"
bytecode="02"
regvalue=""

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
        #print "in listen replica"
        global port_listen_replica,seq_process,transactionID,protocolID,unitID,functioncode,length,bytecode
        s_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_replica.bind((IP, port_listen_replica))
        s_replica.listen(5)
        while 1:
                conn, addr = s_replica.accept()
                data = conn.recv(BUFFER_SIZE)
                #print "received data",data
                if not data: break
                #conn.send(data) #echo
                modbus_response=data.split(",")
                #print "response",modbus_response[0],modbus_response[1],modbus_response[2],
                reg_value=toHex(modbus_response[0])[18:22]
                #print "these should be same",toHex(response),toHex(r.get()),toHex(r.get()),toHex(r.get()) 
                if seq_process < int(modbus_response[1]):
                        response_hex=toHex(modbus_response[0])
                        response=transactionID+protocolID+length+unitID+functioncode+bytecode+reg_value
                        #print "sending resposne",response_hex
                        #print "transaction ID",response_hex[:4],"Protocol ID",response_hex[4:8],"Length",response_hex[8:12],"Unit ID",response_hex[12:14],"function_code",response_hex[14:16],"byte code",response_hex[16:18],"Reg value",response_hex[18:22]
                        #print "must be same",response,response_hex 
                        r.put(binascii.a2b_hex(response))
                        #r.put(response)
                        seq_process=seq_process+1
                        transactionID="000"+str(hex(int(transactionID,16)+1))[2:]
                #print "received response --",toHex(data)
                data=0 #reset the buffer        
                #conn.send()
                #conn.close() 


def listen_master(q,r):
        global port_listen_master,seq_process,transactionID,protocolID,unitID,functioncode
        s_master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_master.bind((IP, 5101))
        s_master.listen(5)
        while 1:
                conn, addr = s_master.accept()
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                #conn.send(data) #echo
                q.put(data)
                #data_hex = toHex(data)
                #print "query",data_hex
                #,"length",data_hex[8:12],
                #,"reference num",data_hex[18:20],"word count",data_hex[20:24]
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

