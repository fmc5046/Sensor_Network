import numpy as np
import matplotlib.pyplot as plt

packet_size = [1,5,10,50,100,216,500,1000,2000,4000,8000,16000]
gzip = [0.04,0.53,1.19,1.81,2.09,2.33,2.49,2.58,2.64,2.68,2.71,2.73]
lzma = [0.02,0.3,0.79,1.71,2.12,2.5,2.82,3.02,3.16,3.26,3.32,3.34]
bz2 = [0.02,0.35,0.84,1.65,1.95,2.21,2.53,2.81,3.08,3.27,3.41,3.52]

g_t = np.array([0.000016,0.000018,0.000022,0.000041,0.000069,0.000124,0.000237,0.00043,0.000745,0.001751,0.004085,0.009069])*1000
g_l = np.array([0.000097,0.000096,0.000096,0.000105,0.000123,0.000172,0.000293,0.000502,0.000806,0.001558,0.00311,0.006184])*1000
g_b = np.array([0.000004,0.000009,0.000018,0.000073,0.000143,0.000318,0.000649,0.00109,0.001531,0.002184,0.003516,0.006276])*1000

plt.figure()
plt.plot(packet_size,gzip,label='gzip')
plt.scatter(packet_size,gzip)

plt.plot(packet_size,lzma,label='lzma')
plt.scatter(packet_size,lzma)

plt.plot(packet_size,bz2,label='bz2')
plt.scatter(packet_size,bz2)

plt.xlabel("Packet Size",fontsize=16)
plt.ylabel("Compression Ratio",fontsize=16)
plt.legend(fontsize=16,loc=4)
plt.xlim([0,1000])

plt.tight_layout()
plt.savefig('cr.svg')
plt.show()




plt.figure()
plt.plot(packet_size,g_t,label='gzip')
plt.scatter(packet_size,g_t)

plt.plot(packet_size,g_l,label='lzma')
plt.scatter(packet_size,g_l)

plt.plot(packet_size,g_b,label='bz2')
plt.scatter(packet_size,g_b)

plt.xlabel("Packet Size",fontsize=16)
plt.ylabel("Compression Time (ms)",fontsize=16)
plt.legend(fontsize=16,loc=2)
plt.xlim([0,1000])
plt.ylim([0,1.5])

plt.tight_layout()
plt.savefig('time.svg')
plt.show()