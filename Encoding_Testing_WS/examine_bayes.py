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

path = "Data/All"
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

snr_new = [float(x) for x in snr]
rssi_new = [float(x) for x in rssi]
num_error_new_byte = [float(x) for x in num_error_byte]

##SNR
min_snr = np.min(snr_new)
max_snr = np.max(snr_new)

slots = int(max_snr) - int(min_snr) + 1
snr_axis = []

#Generate bucket size and snr axis
snr_axis_val = min_snr
buckets = []
all_success = []
all_ecc = []

for i in range(int(slots)):
    buckets.append([])
    all_success.append([])
    all_ecc.append([])

    snr_axis.append(snr_axis_val)
    snr_axis_val += 1

#Sort num_errors into SNR buckets
for i in range(len(num_error_new_byte)):
    snr_tmp = snr_new[i]
    index = int(snr_tmp) + int(abs(min_snr))

    buckets[index].append(float(num_error_new_byte[i]))
    all_success[index].append(success[i])
    all_ecc[index].append(ecc[i])


adaptive_data_rate = []
#Find adaptive data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):
        if buckets[i][j] <= (int(all_ecc[i][j])/2):
            tot += ((200 - int(all_ecc[i][j]))/200)
    if len(buckets[i]) > 0:
        adaptive_data_rate.append(tot/len(buckets[i]))
        

optimal_data_rate = []
#Find optimal data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):
        if buckets[i][j] <= 0:
            tot += 1
        elif buckets[i][j] <= 20:
            tot += ((200 - 40)/200)
        elif buckets[i][j] <= 40:
            tot += ((200 - 80)/200)

    if len(buckets[i]) > 0:
        optimal_data_rate.append(tot/len(buckets[i]))


no_ecc_data_rate = []
#Find No ECC data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):
        if buckets[i][j] <= 0:
            tot += 1

    if len(buckets[i]) > 0:
        no_ecc_data_rate.append(tot/len(buckets[i]))


ecc_40_data_rate = []
#Find ECC 40 data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):
        if buckets[i][j] <= 20:
            tot += ((200 - 40)/200)

    if len(buckets[i]) > 0:
        ecc_40_data_rate.append(tot/len(buckets[i]))


ecc_80_data_rate = []
#Find ECC 80 data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):
        if buckets[i][j] <= 40:
            tot += ((200 - 80)/200)

    if len(buckets[i]) > 0:
        ecc_80_data_rate.append(tot/len(buckets[i]))


ecc_model_data_rate = []
#Find model data rate
for i in range(len(buckets)):
    tot = 0
    for j in range(len(buckets[i])):

        if i - abs(min_snr) > -6:
            ecc_thresh = 0
        elif i - abs(min_snr) > -9:
            ecc_thresh = 20
        else:
            ecc_thresh = 40

        if buckets[i][j] <= ecc_thresh:
            tot += ((200 - ecc_thresh*2)/200)

    if len(buckets[i]) > 0:
        ecc_model_data_rate.append(tot/len(buckets[i]))


plt.figure()

plt.scatter(snr_axis,optimal_data_rate,label="Perfect Knowledge",marker='v')
plt.plot(snr_axis,optimal_data_rate)

plt.scatter(snr_axis,adaptive_data_rate,label="Adaptive Algorithm",marker='D')
plt.plot(snr_axis,adaptive_data_rate)

plt.scatter(snr_axis,ecc_model_data_rate,label="Model Based",marker='D',color='tab:cyan')
plt.plot(snr_axis,ecc_model_data_rate,color='tab:cyan')

#plt.scatter(snr_axis,no_ecc_data_rate,label="No ECC")
#plt.plot(snr_axis,no_ecc_data_rate,'--')

#plt.scatter(snr_axis,ecc_40_data_rate,label="ECC 40")
#plt.plot(snr_axis,ecc_40_data_rate,'--')

#plt.scatter(snr_axis,ecc_80_data_rate,label="ECC 80")
#plt.plot(snr_axis,ecc_80_data_rate,'--')

plt.ylabel("Effective Data Rate")
plt.xlabel("SNR")

plt.legend()

plt.figure()
plt.scatter(snr_new,num_error_new_byte)
plt.ylabel("Number of Byte Errors")
plt.xlabel("SNR")


#Density SNR vs. Num Byte Errors
a = int(slots)
b = int(max(num_error_new_byte)) + 1
z = np.zeros(shape=(a,b))

for i in range(len(num_error_new_byte)):
    x = int(num_error_new_byte[i])
    y = int(snr_new[i]) + 12
    z[y][x] += 1


nx = []
ny = []
nz = []
for i in range(a):
    for j in range(b):
        if z[i][j] > 0:
            nx.append(i - 12)
            ny.append(j)
            nz.append(z[i][j]*10)


fig, ax = plt.subplots()

ax.scatter(nx, ny, s=nz*100)
plt.ylabel("Number of Byte Errors")
plt.xlabel("SNR")


#Density SNR vs. RSSI
a = int(slots)
b = int(abs(min(rssi_new))) + 1 
z = np.zeros(shape=(a,b))

for i in range(len(rssi_new)):
    x = int(abs(rssi_new[i]))
    y = int(snr_new[i]) + 12
    z[y][x] += 1


nx = []
ny = []
nz = []
for i in range(a):
    for j in range(b):
        if z[i][j] > 0:
            nx.append(i - 12)
            ny.append(j*-1)
            nz.append(z[i][j]*10)


fig, ax = plt.subplots()

alpha_arr = nz
color = 'blue'
r, g, b = to_rgb(color)
# r, g, b, _ = to_rgba(color)
color = [(r, g, b, alpha) for alpha in alpha_arr]

ax.scatter(ny, nx, s=nz)
plt.ylabel("SNR")
plt.xlabel("RSSI")


plt.show()