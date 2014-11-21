import sys
dict_num={1:'one',2:'two',3:'three'}

while 1:
	try:
		print dict_num[int(raw_input("Enter the number"))]
	except KeyError:
		print "Not available---"
