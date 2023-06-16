from sim import path_loss
from scipy.stats import binom
import matplotlib.pyplot as plt



prob_b_0 = []
n = 200*8

for d in range(1000,1500,100):
    
    BER = path_loss(d)[0]
    SNR = path_loss(d)[1]
    

    #Binary Channel BER
    #No Error Correction
    p = BER
    prob = binom.cdf(0, n, p)
    prob_b_0.append(prob)

    print(f"The SNR is {SNR} : Probability of arrival {prob} : Distance is {d}")

