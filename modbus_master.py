import pylibmodbus,time,datetime
#port=input("enter port")
def master_poll(ip,port,address,nb):
	times_list=[]
	for i in range (1,4):
		print "in loop"
		before=time.time()
		ls=pylibmodbus.ModbusTcp(ip,port)
		ls.connect()
		#read_data=ls.read_registers(0, 1)
		read_regs=ls.read_input_registers(address,nb)
		for regs in read_regs : print regs
		after=time.time()
		times_list.append(after-before)
		print times_list
		ls.close()
		time.sleep(10)
	print "avg time",reduce(lambda x, y: x + y, times_list) / len(times_list)
master_poll("127.0.0.1",5101,0,1)

