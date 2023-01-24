from numpy import byte
import serial
import time
import sys
import matplotlib.pyplot as plt
from skopt.plots import plot_evaluations

sys.path.append("/home/fred/Lingua_Franca/Playground")
sys.path.append("/home/fred/Lingua_Franca/Hyrdro")

import compress
from node import Node
import stream
import sounddevice as sd
import numpy as np
from skopt.plots import plot_evaluations

ser = serial.Serial('/dev/ttyACM0', 1000000, timeout=0.01)
ser.reset_input_buffer()

#Startup and initialize the object
id = 0 #0 for node that is transmitting data
print(f"Hello world my ID is: {id}")
node = Node(id)
node.init_optimizer()

node.real_class_sensor = True
node.precision = 32
node.new_try_thresh = 50

loop_time = 0.01
val = []

#Initialize mic object
mic = stream.Microphone()
mic.get_stream()

tot_sent = 0

while(node.done == False): 
    
        #Run a loop of the node and update clock
        node.sim_time = time.time_ns()
        out = node.run()

        #If a message is ready to be transmitted send that out
        transmit = out[0]
        val = node.send(transmit)

        #Write to Serial
        if len(val) > 1:
            tot_sent += 1
            print(f"The classifier AoI is: {np.mean(node.aoi_class)/1_000_000_000:.4f}")
            node.number_of_packets += 1
            ser.write(val)
            
            if tot_sent > 100000:
                node.done = True

                print(node.optimizer.get_result())
                plot_evaluations(node.optimizer.get_result())
                plt.show()
        
        #Read serial and add to recive buffer
        read_serial = ser.readline()
        if len(read_serial) > 1:
                #If it contains string than its an ACK
                if '124 156 143' in read_serial.decode():
                        node.ACK_got += 1
                        node.got_ACK = True

                        #print(float(node.ACK_got)/float(node.number_of_packets))
                        #node.recive(read_serial)
                
        #This is where the real sensor gets added
        node.class_sensor.value = mic.get_data()
        node.class_sensor.timestamp = time.time_ns()
        time.sleep(loop_time)


print("Test Done")


