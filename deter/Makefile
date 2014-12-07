CFILE=./broccoli.c
GCC=/usr/bin/gcc
BROCCOLI=/usr/local/bro
all:	$(PROGRAMS)
	cc ./WaterHeater/simulation/modbusServerMain.c ./WaterHeater/simulation/modbusRegisters.c ./WaterHeater/simulation/waterHeaterModel.c -lmodbus -lm -pthread -o server
	cc ./WaterHeater/simulation/modbusCommandClientMain.c -lmodbus -o command_client
	cc ./WaterHeater/simulation/modbusMonitorClientMain.c -lmodbus -o monitor_client

clean:
	rm -f $(PROGRAMS) *.o core                                    
