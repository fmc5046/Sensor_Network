from bdb import effective
from cProfile import label
import csv
from tkinter.ttk import Style
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import binom
from matplotlib.colors import to_rgb, to_rgba

import sys
sys.path.append('/home/fred/Lingua_Franca/Recover/Time_Varying_Channel_WS')


def percentage_below_threshold(lst, threshold):
    """
    Returns the percentage of values in lst that are below the threshold.
    """
    count = sum(1 for x in lst if x < threshold)
    return count / len(lst) if len(lst) > 0 else 0


ratio = []
rssi = []
snr = []
num_trans = []
num_rep = []
num_error_byte = []
success = []
ecc = []
timestamp = []

path = "Data/aoi"
arr = os.listdir(path)

for file in arr:
    file_name = str(path) + "/" + str(file)
    print(file_name)
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ratio.append(row[0])
            rssi.append(row[1])
            snr.append(row[2])
            num_trans.append(row[3])
            num_rep.append(row[4])
            num_error_byte.append(row[5])
            success.append(row[6])
            ecc.append(row[7])
            timestamp.append(row[8])

snr = [float(x) for x in snr]
rssi = [float(x) for x in rssi]
num_error_byte = [float(x) for x in num_error_byte]
timestamp = [float(x) for x in timestamp]

aoi = []
at = []
aut = []

ut = timestamp[0]
print(ut)
t = timestamp[0]
last = timestamp[0]
for i in range(1,len(timestamp)):

    t = timestamp[i]
    ut = min(ut + 1.35,t)
    
    at.append(t)
    aut.append(ut)
    aoi.append(t - ut)

    print(last - t)

    last = t



plt.figure()
plt.plot(at)

plt.figure()
plt.plot(aut)

plt.figure()
plt.plot(aoi)
plt.show()

