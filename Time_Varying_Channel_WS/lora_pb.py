from cProfile import label
from turtle import distance
from sim import Pb_AWGN, path_loss,Pb_Ray
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

def m_to_dB(A):
    return 20*np.log10(A)

SF = 7
Ts = np.linspace(-30,25,100)
p = []
p_ray = []

T = []

prob_b_0 = []

n = 200*8

for t in Ts:

    Pb = Pb_AWGN(t)
    p.append(Pb)

    Pb_ray = Pb_Ray(t)
    p_ray.append(Pb_ray)

    prob = binom.cdf(0, n, Pb)
    prob_b_0.append(prob)

plt.figure()
plt.plot(Ts,prob_b_0)


plt.figure()

plt.plot(Ts,p,label="AWGN Channel Model")
plt.plot(Ts,p_ray,label="Rayleigh Channel Model")

plt.yscale('log')
plt.xlabel("SNR")
plt.ylabel("Probability of Bit Error")
plt.legend()

plt.show()