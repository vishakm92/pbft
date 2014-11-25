#!/usr/bin/env python

import socket,sys,multiprocessing

failures = (int(sys.argv[2]) -1) /3 #value of f iin algorithm
preprepare={} #dictionary which has (seq,[message,count]) of preprepare messages
prepare={} #dictionary which has (seq,count) of prepare messages
commit={} #dictionary which has (seq,m) of commit messages

TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
print "Server listening in port ", TCP_PORT
server_id=TCP_PORT-5000
BUFFER_SIZE = 20    # Normally 1024, but we want fast response
port_client=5100


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

def toHex(s):
        lst = []
        for ch in s:
                hv = hex(ord(ch)).replace('0x', '')
                if len(hv) == 1:
                        hv = '0'+hv
                lst.append(hv)
        return reduce(lambda x,y:x+y, lst)


def send_to_slave(commit_q,response_q):      
    s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_local.connect((TCP_IP, 502))
    s_local.send(commit_q.get())
    data=s_local.recv(BUFFER_SIZE)
    print "response from the slave",data
    response_q.put(data)


def commit_message_fn(commit_q,response_q): 
    print "in commit thread"
    global port_client
    while 1:    
        if not commit_q.empty():
            send_to_slave(commit_q,response_q)
    	    s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	    s_local.connect((TCP_IP, port_client))
    	    print "sending response to client"
            s_local.send(response_q.get())

def process_message_fn(msg_q,prepare_q,commit_q):
    while 1:
        data=msg_q.get()
        if data.startswith("Preprepare"):
            #Preprepare message format <preprepare,seq,m>
            message=data.split(",")
            seq=int(message[1])
            m=message[2]
            if seq in preprepare.keys():
                preprepare[seq] = preprepare[seq][1] + 1
                sendall("Prepare,"+str(seq)+","+str(server_id))
            else:
                preprepare[seq]=[m,0]
                sendall("Prepare,"+str(seq)+","+str(server_id))
        elif data.startswith("Prepare"):
            #Prepare message format <Prepare,seq,i>
            message=data.split(",")
            seq=int(message[1])
            if seq in prepare.keys():
                prepare[seq] = prepare[seq] + 1
            else:
                prepare[seq]=1
            
            #if seen 2*f prepares, then go to  prepared state
			#Commit message format <Commit,seq,i>
            if prepare[seq] == 2*failures:
                prepare[seq]=0
                sendall("Commit,"+str(seq)+","+str(server_id))
                message=data.split(",")
                seq=int(message[1])
                commit[seq]=preprepare[seq][0]
                commit_q.put(commit[seq])
                sendall("Commit,"+str(seq)+","+str(server_id))
                print "Message commited - with sequence",seq,"content - ",preprepare[seq][0]


def sendall(message):
    TCP_IP = '127.0.0.1'
    BUFFER_SIZE = 1024
                            #send preprepare to all ports
    for i in range(int(sys.argv[2])+1):
        if not i == server_id: # dont send to itself
            PORT = 5000+i
            #print "sending ",message,"to port",PORT
            s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_local.connect((TCP_IP, PORT))
            s_local.send(message)
            #data=s_local.recv(BUFFER_SIZE) #echo
            #s_local.close()


def read_thread(q):
    print "server id",server_id,"number of replica",sys.argv[2]
    while 1:
        conn, addr = s.accept()
    #print 'Client Connected at', addr
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        #conn.send(data) #echo
        print "Received ",data
        q.put(data)
        #conn.close()
        data=0#reset the data

queue = multiprocessing.Queue()
prepare_queue=multiprocessing.Queue()
commit_queue=multiprocessing.Queue()
response_queue=multiprocessing.Queue()

p = multiprocessing.Process(target=read_thread, args=(queue,))
p.start()

leader = multiprocessing.Process(target=process_message_fn, args=(queue,prepare_queue,commit_queue,))

commit_thread = multiprocessing.Process(target=commit_message_fn, args=(commit_queue,response_queue))

commit_thread.start()
leader.start()
leader.join()
commit_thread.join()
p.join()
