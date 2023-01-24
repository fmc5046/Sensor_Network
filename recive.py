from numpy import byte
import serial
import time
import sys

sys.path.append("/home/fred/Lingua_Franca/Playground")
sys.path.append("/home/fred/Lingua_Franca/Hyrdro")

import compress
from node import Node
import stream
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.01)
ser.reset_input_buffer()

loop_time = 0.01

#Startup and initialize the object
id = 1 #0 for node that is transmitting data and 1 for the gateway
print(f"Hello world my ID is: {id}")
node = Node(id)
node.init_optimizer()

while(True):

    #Read serial and add to recive buffer
    read_serial = ser.readline()
    if len(read_serial) > 1:
        print(read_serial)
        node.recive(read_serial)

    #Run a loop of the node
    out = node.run()

    #If something has been output for an application, its audio so play it
    clip = out[1]
    if len(clip) > 10 and 0:
        print("Got to play audio")
        samplerate = int(44100*1)
        sd.play(clip, samplerate)

        file = "test.wav"
        sample = int(44100*0.65)
        d = np.array(clip,dtype=np.float64)
        wav.write(file,sample,d)   
        break 

    transmit = out[0]
    val = node.send(transmit)
    #Write to Serial
    if len(val) > 1:
        ser.write(val)
 
    time.sleep(loop_time)



