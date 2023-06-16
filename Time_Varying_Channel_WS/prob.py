import matplotlib.pyplot as plt
from scipy.special import lambertw
import numpy as np

SNR_points = [8.5,7,5.9,5]
pa_points = [0.97,0.87,0.63,0.3]
pa_points = np.linspace(0.1,0.97,5)


#From Sim
sim = [40.2,135.7,339.9,628]
sim2 = [146,447,1132,2162]
sim2 = [x / 1 for x in sim2]

mu = 1
lam = 0.25

all_delta = []
all_lam = []
all_mu = []
all_p = []
all_o = []

#np.linspace(0,1,num=20)
for pa in pa_points:

    mu = pa
    p = lam/mu
    delta = (1/mu)*(1 + (1/p) + ((p**2)/(1-p)))

    y = -1*p*lambertw((-1/p)*np.e**(-1/p))
    o_delta = (1/(2*mu))*(1 + (1/(1 - y)))

    all_o.append(o_delta*100)
    all_delta.append(delta*100)
    all_lam.append(lam)
    all_mu.append(mu)
    all_p.append(pa)

plt.figure()
plt.plot(all_p,all_o,label="DM1")
plt.scatter(all_p,all_o)
#plt.plot(all_p,sim,label="Sim")
#plt.scatter(all_p,sim)
plt.legend()
plt.xlabel("p_a")
plt.ylabel("AoI")
plt.savefig("Theo_Sim_AoI.pdf",format='pdf')
plt.show()
