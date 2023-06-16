from cProfile import label
from sim import path_loss
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

B = 915e6
C = []
SNR = []

ECC = 0
n = 200*8
k = n - ECC
x = ECC/2

prob_b_0 = []
prob_b_20 = []
prob_b_40 = []

prob_mc_0 = []
prob_mc_20 = []
prob_mc_40 = []

SNR_tot = []

for d in range(1000,3000,50):
    
    BER = path_loss(d)[0]
    
    #Binary Channel BER
    #No Error Correction
    p = BER
    prob = binom.cdf(0, n, p)
    prob_b_0.append(prob)

    #No Error Correction
    p = BER
    prob = binom.cdf(20, n, p)
    prob_b_20.append(prob)

    #Rayleigh Channel BER
    #No Error Correction
    p = BER
    prob = binom.cdf(40, n, p)
    prob_b_40.append(prob)

    #No Error Correction
    SNR = path_loss(d)[1]
    p = 0.5*(1 - np.sqrt(SNR/(SNR + 1)))
    prob = binom.cdf(0, n, p)
    prob_mc_0.append(prob)

    #ECC 20
    p = 0.5*(1 - np.sqrt(SNR/(SNR + 1)))
    prob = binom.cdf(20, n, p)
    prob_mc_20.append(prob)

    #ECC 40
    p = 0.5*(1 - np.sqrt(SNR/(SNR + 1)))
    prob = binom.cdf(40, n, p)
    prob_mc_40.append(prob)

    SNR_tot.append(SNR)

plt.figure()
#plt.plot(SNR_tot,prob_b,label="Binary Channel Model")
plt.plot(SNR_tot,prob_b_0,label="AWGN Chanel Model ECC 0")
#plt.plot(SNR_tot,prob_b_20,label="AWGN Chanel Model ECC 20")
#plt.plot(SNR_tot,prob_b_40,label="AWGN Chanel Model ECC 40")
plt.xlabel("SNR (dB)")
plt.ylabel("Probability of Successful Decode")
#plt.xscale('log')
#plt.yscale('log')
#plt.legend()
plt.show()


for d in range(1000,5000,20):
    tmp_SNR = path_loss(d)[1]
    C.append(B*np.log2(1 + tmp_SNR))
    SNR.append(tmp_SNR)


plt.figure()
plt.plot(SNR,C)
