import numpy as np
import matplotlib.pyplot as plt

a = np.convolve([1,1,0,1,1,0,0,0,0,1,1,0,1,0,0,1], [1,0,0,1,0,1,1,0,0,0,0,0,1,0,1,1])

plt.figure()
plt.plot(a)
plt.show()