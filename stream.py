#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.

"""
import argparse
import queue
import sys

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import time

class Microphone():

    def __init__(self): 
        self.stream = []
        self.q = queue.Queue()
        self.b = []

    def get_stream(self):    
        # by default we open the device stream with all the channels
        # (interleaved in the data buffer)

        device_list = sd.query_devices()

        for d in device_list:
            if d['name'] == 'U-22: USB Audio (hw:1,0)':
                device = d

        print(device)
        print(device['index'])

        audio_stream = sd.InputStream(
            samplerate=44100,
            blocksize=10,
            device=device['index'],
            channels = device['max_input_channels'],
            dtype= np.int16,
            callback=self.audio_callback)

        self.stream = audio_stream


    def audio_callback(self,indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        #print(f"In data {indata}")
        self.q.put(indata)

        a = self.q.get_nowait()
        c = list(np.array(a[:,0]).flat)
        for i in c:
            self.b.append(np.float32(i/32767))

    def get_data(self):
        self.b = []
        self.stream.start()
        time.sleep(0.01)
        self.stream.stop()

        return self.b[::1]


