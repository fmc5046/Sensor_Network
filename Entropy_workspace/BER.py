import fpzip
import numpy as np
import soundfile as sf
import struct
import random
import matplotlib.pyplot as plt


points = [10,12,18,24,32]
BER = [0.03126277193,0.02683265747,0.02097361169,0.008192891782,0]

plt.plot(points,BER)
plt.scatter(points,BER)

plt.title("BER vs Bit Precision of FPZIP Compression",fontsize=16)
plt.xlabel("Bit Precision",fontsize=16)
plt.ylabel("BER",fontsize=16)

plt.tight_layout()
plt.savefig('foo.svg')
plt.show()
