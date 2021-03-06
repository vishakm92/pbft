#!/usr/bin/env python

#Messages
#<preprepare,seq,m>
#<Prepare,seq,i>
#<Commit,seq,i>
#<LeaderChange>

import socket,sys,multiprocessing
leader_id=0

no_slaves=int(sys.argv[2])
failures = (no_slaves -1) /3 #value of f iin algorithm
preprepare={} #dictionary which has (seq,message) of preprepare messages
prepare={} #dictionary which has (seq,count) of prepare messages
commit={} #dictionary which has (seq,m) of commit messages

TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
print "Server listening in port ", TCP_PORT
server_id=TCP_PORT-5000
BUFFER_SIZE = 1024    # Normally 1024, but we want fast response
port_client=5100
seq_no=1

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


def send_preprepare(q):
        global seq_no
        #print "in send preprepare function"
        TCP_IP = '127.0.0.1'
        BUFFER_SIZE = 1024
        while 1:
                #send preprepare to all ports
                MESSAGE = q.get()
                client_port=q.get()

                if not (( MESSAGE.startswith("Prepare")) or ( MESSAGE.startswith("Commit"))):
                        #print "going to broadcast",MESSAGE
                        sendall("Preprepare,"+str(seq_no)+","+MESSAGE)
                        seq_no=seq_no+1

def send_to_slave(commit_q,response_q):      
    data=commit_q.get()
    data_list=data.split(",")
    query=data_list[0]
    seq=data_list[1]
    #print "data in commit ",toHex(data)
    s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_local.connect((TCP_IP, 502))
    s_local.send(query)
    data=s_local.recv(BUFFER_SIZE)
    reg_value=toHex(data)[18:22]
    #print "response from the slave",toHex(data)
    response_q.put(data+","+seq+","+str(server_id))


def commit_message_fn(commit_q,response_q): 
    #print "in commit thread"
    global port_client
    while 1:    
        if not commit_q.empty():
            #print "in commit "
            send_to_slave(commit_q,response_q)
            s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_local.connect((TCP_IP, port_client))
            #print "sending response to client"
            response=response_q.get()
            s_local.send(response)
            #print "sent to client",toHex(response)

def process_message_fn(msg_q,prepare_q,commit_q):
    global leader_id,server_id,seq_no    
    if server_id == leader_id:
        print "leader process!!!"
    while 1:
        data=msg_q.get()
        if server_id == leader_id:
            if not (( data.startswith("Prepare")) or ( data.startswith("Commit"))):
                print "going to broadcast",data
                sendall("Preprepare,"+str(seq_no)+","+data)
                seq_no=seq_no+1

        if data.startswith("Preprepare"):
            #Preprepare message format <preprepare,seq,m>
            message=data.split(",")
            seq=int(message[1])
            m=message[2]
            #if seq in preprepare.keys():
    #   print "gone!!"
         #       preprepare[seq] = preprepare[seq][1] + 1
          #      sendall("Prepare,"+str(seq)+","+str(server_id))
           # else:
            preprepare[seq]=m
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
                if seq in preprepare.keys():
                    query=preprepare[seq]
                    #commit[seq]=preprepare[seq]
                    commit_q.put(query+","+str(seq))
                    sendall("Commit,"+str(seq)+","+str(server_id))
                    print "Message commited - with sequence",seq,"content - ",query
        elif data.startswith("LeaderChange"):
            if leader_id == server_id:
                print "not leader anymore"
            leader_id=(leader_id+1)%no_slaves


def sendall(message):
    TCP_IP = '127.0.0.1'
    BUFFER_SIZE = 1024
                            #send preprepare to all ports
    for i in range(no_slaves+1):
        if not (i == server_id): # dont send to itself 
            PORT = 5000+i
            #print "sending ",message,"to port",PORT
            s_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s_local.settimeout(1)
            s_local.connect((TCP_IP, PORT))
            s_local.send(message)
            #data=s_local.recv(BUFFER_SIZE) #echo
            s_local.close()


def read_thread(q):
    #print "server id",server_id,"number of replica",sys.argv[2]
    while 1:
        conn, addr = s.accept()
    #print 'Client Connected at', addr
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        #conn.send(data) #echo
        #print "Received ",data
        q.put(data)
        #conn.close()
        data=0#reset the data

queue = multiprocessing.Queue()
prepare_queue=multiprocessing.Queue()
commit_queue=multiprocessing.Queue()
response_queue=multiprocessing.Queue()

p = multiprocessing.Process(target=read_thread, args=(queue,))
p.start()

process_msg = multiprocessing.Process(target=process_message_fn, args=(queue,prepare_queue,commit_queue))

commit_thread = multiprocessing.Process(target=commit_message_fn, args=(commit_queue,response_queue))

commit_thread.start()
process_msg.start()
process_msg.join()
commit_thread.join()
p.join()
