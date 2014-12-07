#!/bin/bash
gnome-terminal --tab -e "bash -c \"sh non_leaders.sh $1; exec bash\""
gnome-terminal --tab -e "bash -c \"python client.py; exec bash\""
#gnome-terminal --tab -e "bash -c \"sudo ./WaterHeater/server -p 502; exec bash\""

