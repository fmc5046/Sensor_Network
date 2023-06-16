from cProfile import label
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import binom

import sys
sys.path.append('/home/fred/Lingua_Franca/Recover/Time_Varying_Channel_WS')
from sim import Pb_AWGN


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
num_error = []
num_error_byte = []

path = "Data/Stair_Data_w_byte"
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
            num_error.append(row[5])
            num_error_byte.append(row[6])

snr_new = [float(x) for x in snr]
rssi_new = [float(x) for x in rssi]
num_error_new = [float(x) for x in num_error]
num_error_new_byte = [float(x) for x in num_error_byte]


##SNR
min_snr = np.min(snr_new)
max_snr = np.max(snr_new)

print(min_snr)
print(max_snr)

slots = abs(min_snr) + abs(max_snr) + 1
snr_axis = []

#Generate bucket size and snr axis
snr_axis_val = min_snr
buckets = []
for i in range(int(slots)):
    buckets.append([])
    snr_axis.append(snr_axis_val)
    snr_axis_val += 1

#Sort num_errors into SNR buckets
for i in range(len(num_error_new)):
    snr_tmp = snr_new[i]
    index = int(snr_tmp) + int(abs(max_snr))

    buckets[index].append(float(num_error_new[i]))

num_error_means = []
ber = []
#Calculate list of mean values
for i in range(len(buckets)):
    num_error_means.append(np.mean(buckets[i], axis=0))
    ber.append(np.mean(buckets[i], axis=0)/(200*8))


##RSSI
min_rssi = np.min(rssi_new)
max_rssi = np.max(rssi_new)

slots = abs(min_rssi) - abs(max_rssi) + 1
rssi_axis = []

#Generate bucket size and RSSI axis
rssi_axis_val = min_rssi
buckets = []
for i in range(int(slots)):
    buckets.append([])
    rssi_axis.append(rssi_axis_val)
    rssi_axis_val += 1

#Sort num_errors into RSSI buckets
for i in range(len(num_error_new)):
    rssi_tmp = rssi_new[i]
    index = int(rssi_tmp) + int(abs(max_rssi))
    buckets[index].append(float(num_error_new[i]))

num_error_means_rssi = []
ber_rssi = []
#Calculate list of mean values
for i in range(len(buckets)):
    num_error_means_rssi.append(np.mean(buckets[i], axis=0))
    ber_rssi.append(np.mean(buckets[i], axis=0)/(200*8))

#This calculates the effective data rate vs RSSI
rssi_thresh = range(-130,-40,5)
eff_no = []
eff_ecc_10 = []
eff_ecc_20 = []
eff_ecc_40 = []
eff_ecc_80 = []

ax = []

for val in rssi_thresh:

    rssi_thresh_low = val
    rssi_thresh_high = rssi_thresh_low + 5

    e10 = (210 - 10)/210
    e20 = (210 - 20)/210
    e40 = (210 - 40)/210
    e80 = (210 - 80)/210

    byte_error_high = []
    for i in range(len(rssi_new)):
        if rssi_new[i] < rssi_thresh_high and rssi_new[i] > rssi_thresh_low:
            byte_error_high.append(num_error_new_byte[i])

    eff_no.append(percentage_below_threshold(byte_error_high,1) * 1)
    eff_ecc_10.append(percentage_below_threshold(byte_error_high,5 + 1) * e10)
    eff_ecc_20.append(percentage_below_threshold(byte_error_high,10 + 1) * e20)
    eff_ecc_40.append(percentage_below_threshold(byte_error_high,20 + 1) * e40)
    eff_ecc_80.append(percentage_below_threshold(byte_error_high,40 + 1) * e80)
    ax.append(val)





#This calculates the effective data rate SNR
snr_thresh = range(int(min_snr),int(max_snr))
eff_no = []
eff_ecc_10 = []
eff_ecc_20 = []
eff_ecc_40 = []
eff_ecc_80 = []

num_no = []
num_20 = []
num_40 = []
num_80 = []

ax = []

for val in snr_thresh:

    e10 = (210 - 10)/210
    e20 = (210 - 20)/210
    e40 = (210 - 40)/210
    e80 = (210 - 80)/210

    byte_error_high = []
    for i in range(len(snr_new)):
        if int(snr_new[i]) == val:
            byte_error_high.append(num_error_new_byte[i])

    eff_no.append(percentage_below_threshold(byte_error_high,1) * 1)
    eff_ecc_10.append(percentage_below_threshold(byte_error_high,5 + 1) * e10)
    eff_ecc_20.append(percentage_below_threshold(byte_error_high,10 + 1) * e20)
    eff_ecc_40.append(percentage_below_threshold(byte_error_high,20 + 1) * e40)
    eff_ecc_80.append(percentage_below_threshold(byte_error_high,40 + 1) * 1)
    ax.append(val)


    num_no.append((percentage_below_threshold(byte_error_high,1) + 0.001))
    num_20.append((percentage_below_threshold(byte_error_high,10 + 1) + 0.001))
    num_40.append((percentage_below_threshold(byte_error_high,20 + 1) + 0.001))
    num_80.append((percentage_below_threshold(byte_error_high,40 + 1) + 0.001))


plt.figure()
#plt.title("RSSI vs Effective Data")
plt.plot(ax,eff_no,label = "No ECC")
plt.scatter(ax,eff_no)
#plt.plot(ax,eff_ecc_10,label = "ECC 10")
#plt.scatter(ax,eff_ecc_10)
plt.plot(ax,eff_ecc_20,label = "ECC 20")
plt.scatter(ax,eff_ecc_20)
#plt.plot(ax,eff_ecc_40,label = "ECC 40")
#plt.scatter(ax,eff_ecc_40)
plt.plot(ax,eff_ecc_80,label = "ECC 80")
plt.scatter(ax,eff_ecc_80)
plt.xlabel("SNR (dB)")
plt.ylabel("Normalized Data Rate")
plt.legend()

plt.figure()
#plt.title("SNR vs Effective Data Rate")
plt.plot(ax,eff_no,label = "Measured")
plt.scatter(ax,eff_no)
#plt.plot(ax,eff_ecc_20,label = "Measured ECC 20")
#plt.scatter(ax,eff_ecc_20)
#plt.plot(ax,eff_ecc_40,label = "Measured ECC 40")
#plt.scatter(ax,eff_ecc_40)
#plt.plot(ax,eff_ecc_80,label = "Measured ECC 80")
#plt.scatter(ax,eff_ecc_80)
plt.xlabel("SNR (dB)")
plt.ylabel("Probability of Packet Arrival")
#plt.legend()


SF = 7
Ts = np.linspace(-13,10,100)
p = []
T = []

prob_b_0 = []
prob_b_10 = []
prob_b_20 = []
prob_b_40 = []

n = 200*8

for t in Ts:

    Pb = Pb_AWGN(t)
    p.append(Pb)

    prob = binom.cdf(0, n, Pb)
    prob_b_0.append(prob)

    prob = binom.cdf(10, n, Pb)
    prob_b_10.append(prob)

    prob = binom.cdf(20, n, Pb)
    prob_b_20.append(prob)

    prob = binom.cdf(40, n, Pb)
    prob_b_40.append(prob)


plt.plot(Ts,prob_b_0,label="Closed Form Expression",color='tab:blue',linestyle="--")
#plt.plot(Ts,prob_b_10,label="Closed Form Expression ECC 20")
#plt.plot(Ts,prob_b_20,label="Closed Form Expression ECC 40")
#plt.plot(Ts,prob_b_40,label="Closed Form Expression ECC 80",color='tab:orange',linestyle="--")
#plt.title("Effective Data Rate vs. RSSI")

plt.legend()

plt.figure()
plt.plot(ax,num_no, label = "Measured ECC 0")
plt.scatter(ax,num_no)
plt.plot(ax,num_20, label = "Measured ECC 20")
plt.scatter(ax,num_20)
plt.plot(ax,num_40, label = "Measured ECC 40")
plt.scatter(ax,num_40)
plt.plot(ax,num_80, label = "Measured ECC 80")
plt.scatter(ax,num_80)
plt.xlabel("SNR")
plt.ylabel("Number of Packets to Transmit Data Normalized")

plt.legend()

plt.figure()
plt.plot(snr_axis,ber,label="Measured")
plt.scatter(snr_axis,ber)
plt.ylabel("Number of Packets to Transmit Normalized")

plt.figure()
plt.title("SNR vs. BER")
plt.plot(snr_axis,ber,label="Measured")
plt.scatter(snr_axis,ber)
plt.plot(Ts,p,label="Theoretical")
plt.legend()
plt.yscale('log')
plt.xlabel("SNR")
plt.ylabel("BER")

plt.figure()
plt.title("RSSI vs. BER")
plt.plot(rssi_axis,ber_rssi)
plt.scatter(rssi_axis,ber_rssi)
plt.yscale('log')
plt.xlabel("RSSI")
plt.ylabel("BER")

plt.figure()
plt.title("SNR vs. Number of Bit Errors")
plt.scatter(snr_new,num_error_new)
plt.plot(snr_axis,num_error_means,'r')
plt.xlabel("SNR")
plt.ylabel("Number of Errors in Message")

plt.figure()
plt.title("RSSI vs. Number of Bit Errors")
plt.scatter(rssi_new,num_error_new)
plt.plot(rssi_axis,num_error_means_rssi,'r')
plt.xlabel("RSSI")
plt.ylabel("Number of Errors in Message")

plt.figure()
plt.title("SNR vs. Number of Byte Errors")
plt.scatter(snr_new,num_error_new_byte)
plt.xlabel("SNR")
plt.ylabel("Number of Errors in Message")

plt.figure()
plt.title("RSSI vs. Number of Byte Errors")
plt.scatter(rssi_new,num_error_new_byte)
plt.xlabel("RSSI")
plt.ylabel("Number of Errors in Message")

plt.figure()
plt.title("SNR vs. RSSI")
plt.scatter(rssi_new,snr_new)
plt.xlabel("RSSI")
plt.ylabel("SNR")


plt.show()

