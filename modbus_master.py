import pylibmodbus,time,datetime
times_pbft=[]
#port=input("enter port")
for i in range (1,4):
	print "in loop"
	before=time.time()
	ls=pylibmodbus.ModbusTcp("127.0.0.1",5101)
	ls.connect()
	#read_data=ls.read_registers(0, 1)
	read_bits=ls.read_bits(0,1)
	print read_bits[0]
	after=time.time()
	times_pbft.append(after-before)
	print times_pbft
	ls.close()
	time.sleep(20)
print "avg time pbft",reduce(lambda x, y: x + y, times_pbft) / len(times_pbft)
times_reg=[]
for i in range (1,4):
        print "in loop"
        before=time.time()
        ls=pylibmodbus.ModbusTcp("127.0.0.1",502)
        ls.connect()
        #read_data=ls.read_registers(0, 1)
        read_bits=ls.read_bits(0,1)
        print read_bits[0] 
        after=time.time() 
        times_reg.append(after-before)
        print times_reg 
        ls.close() 
print "avg time regular",reduce(lambda x, y: x + y, times_reg) / len(times_reg)

