import numpy as np
import matplotlib.pyplot as plt

packet_size = [1,5,10,50,100,216,500,1000]
fp20 = [0.05,0.66,1.83,3.89,4.61,5.18,5.56,5.75]
fp14 = [0.06,0.73,2.19,6.28,8.44,10.58,12.2,13.06]

g_20 = np.array([0.00001,0.000011,0.000012,0.000015,0.000018,0.000024,0.000039,0.000063])*1000
g_14 = np.array([0.00001,0.000011,0.000012,0.000014,0.000017,0.000022,0.000034,0.000054])*1000

plt.figure()
plt.plot(packet_size,fp20,label='FPZIP 20-bit precision')
plt.scatter(packet_size,fp20)

plt.plot(packet_size,fp14,label='FPZIP 14-bit precision')
plt.scatter(packet_size,fp14)

plt.xlabel("Packet Size",fontsize=16)
plt.ylabel("Compression Ratio",fontsize=16)
plt.legend(fontsize=16,loc=4)
plt.xlim([0,1000])

plt.tight_layout()
plt.savefig('cr.svg')
plt.show()

plt.figure()
plt.plot(packet_size,g_20,label='FPZIP 20-bit precision')
plt.scatter(packet_size,g_20)

plt.plot(packet_size,g_14,label='FPZIP 14-bit precision')
plt.scatter(packet_size,g_14)

plt.xlabel("Packet Size",fontsize=16)
plt.ylabel("Compression Time (ms)",fontsize=16)
plt.legend(fontsize=16,loc=2)
plt.xlim([0,1000])
#plt.ylim([0,1.5])

plt.tight_layout()
plt.savefig('time.svg')
plt.show()