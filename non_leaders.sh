#!/bin/bash
count=1
#while [ $count -le $1 ]
#do
echo "Welcone $count times"
port=5000+$count
echo port
gnome-terminal -x "python server_non_leader.py 5000"
#count=$(( count+1 ))	 # increments $n
#done
