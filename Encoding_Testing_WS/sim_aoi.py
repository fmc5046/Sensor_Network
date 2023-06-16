from cProfile import label
from sqlite3 import Timestamp
import numpy as np
from scipy import special as sp
import matplotlib.pyplot as plt
import random
from scipy.stats import binom
from scipy.special import lambertw


def qfunc(x):
    return 0.5-0.5*sp.erf(x/np.sqrt(2))

def Pb_AWGN(SNR):

    SF = 7
    two_SF = 2**(SF+1)
    T = 10**(SNR/10)

    a = (T*two_SF)**0.5
    b = (1.386*SF + 1.154)**0.5

    return qfunc(a - b)



time_max = 50000
step = 3

plt.figure()

for ECC in list([0,80]):

    aaoi = []
    theory_aaoi = []
    all_prob = []
    coding_rate = (200 - ECC)/200
    arrival_rate = []
    print(coding_rate)

    for SNR in np.linspace(-13,10,20):


        #Calculate Theory
        prob = binom.cdf(ECC, 200*8, Pb_AWGN(SNR))
        mu = prob

        
        lam = (1/step) * (1/coding_rate)
        p = lam/mu

        y = -1*p*lambertw((-1/p)*np.e**(-1/p))
        delta = (1/(2*mu))*(1 + (1/(1 - y)))

        theory_aaoi.append(abs(delta))

        #Reinitialize Sim
        current_time = 0
        timestamp = current_time
        aoi = []
        buffer = []

        all_prob.append(prob)
        arrive = []

        for i in range(time_max):

            #Add to buffer every n steps
            if current_time % step == 0:
                buffer.append(current_time)

            #If successful transmission
            if random.random() <= prob and len(buffer) > 0:
                timestamp = buffer.pop(0)
                arrive.append(1)
            else:
                arrive.append(0)

            aoi.append(current_time - timestamp)

            #Increment time
            current_time += 1

        #print(f"Probability of Arrival: {prob} and the SNR is {SNR} Average AoI: {np.mean(aoi)}")

        aaoi.append(np.mean(aoi))
        arrival_rate.append(np.mean(arrive))

    #plt.plot(all_prob,aaoi,label="Simulation ECC " + str(ECC))
    #plt.scatter(all_prob,aaoi)

    plt.plot(all_prob,arrival_rate,label="Simulation ECC " + str(ECC))
    plt.scatter(all_prob,arrival_rate)

    #plt.plot(all_prob,theory_aaoi,label="Theory DM1 ECC " + str(ECC))
    #plt.scatter(all_prob,theory_aaoi)

plt.ylabel("Probability of Arrival")
plt.xlabel("SNR")

#plt.ylim([0,10])
#plt.xlim([-8,0])

plt.legend()
plt.show()
