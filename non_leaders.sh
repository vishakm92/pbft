#!/bin/bash
count=1

while [ $count -le $1 ]
do
	echo "Welcone $count times"
	port=$(( count+5000))
	echo $port
	#cmd+=( --tab -e "python server_non_leader.py 5000" )
	#x-terminal-emulator -e python server_non_leader.py 5000 
	gnome-terminal --tab -e "bash -c \"python server_non_leader.py $port $1; exec bash\""
	count=$(( count+1 ))	 # increments $n
done
