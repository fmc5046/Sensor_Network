from ctypes import sizeof
import numpy as np
from pyldpc import make_ldpc, encode, decode, get_message
import struct
import matplotlib.pyplot as plt
import math

from scipy import rand

def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

def float_to_bit_array(float_num):
    buf = struct.pack('%sf' % len(float_num), *float_num)

    encoded = bytearray(buf)

    bit_array = []
    for i in encoded:
        bitstr = bin(i)[2:].zfill(8)
        for j in bitstr:
            if int(j) == 1:
                bit_array.append(1)
            else:
                bit_array.append(0)

    return bit_array

def bitstring_to_bytes(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def bits_to_float(bits):
    bit_str = ""
    for i in bits:
        bit_str += str(i)
    tmp = bitstring_to_bytes(bit_str)
    decoded = tmp

    chunks = divide_chunks(decoded,4)
    decoded_float = []
    for i in chunks:
        decoded_float.append(float(struct.unpack('f', i)[0]))

    return decoded_float

def path_loss(d):

    f = 915e6

    Lfs_dB = (20*np.log10(d) + 20*np.log10(f) - 147.55)
    Lfs = 10**(Lfs_dB/10)

    Pr = 1/max(Lfs,1e-30)

    N0_dBm = -101
    N0_dB = N0_dBm
    N0 = 10**(N0_dB/10)

    SNR = Pr/N0

    BER = 0.5*math.erfc(np.sqrt(SNR))

    return BER,SNR

tot_r = []
tot_ar = []
all_SNR = []

n = 24*3
d_v = 2
d_c = 8
snr = 20

p = 3
ds = np.linspace(1_000,4_000,10)  

for d in ds:

    H, G = make_ldpc(n, d_v, d_c, systematic=True, sparse=True)
    k = G.shape[1]
    seed = 42
    
    p_size = 200
    float_num = int(((1 - (d_v/d_c))*p_size)/4)

    nums = np.random.rand(float_num)
    v = np.array(float_to_bit_array(nums))
    img_shape = v.shape
    v = v.flatten()

    n_bits_total = v.size
    n_blocks = n_bits_total // k
    residual = n_bits_total % k
    if residual:
        n_blocks += 1

    resized_img = np.zeros(k * n_blocks)
    resized_img[:n_bits_total] = v    

    sucess = 0 
    m = 100

    for j in range(m):
        y = encode(G, resized_img.reshape(k, n_blocks), 1000, seed)


        BER = path_loss(d)[0]
        error_percent = 1/max(BER,1e-10)
        
        for i in range(len(y)):
            r = np.random.randint(error_percent)
            if (r == 0):
                y[i] = 0
        
        de = decode(H, y, snr)
        x = np.array([get_message(G, de[:, i]) for i in range(n_blocks)]).T
        x = x.flatten()[:np.prod(img_shape)]
        x = x.reshape(*img_shape)

        not_same = False
        for i in range(len(v)):
            if v[i] != x[i]:
                not_same = True
        if not_same == False:
            sucess += 1
            
    print(f"There are {float_num} float numbers in this packet Crossover Probability is {p/10.0} and packet size is {np.size(y)} bits and distance is {d}")
    print(f"The Theory Rate is {1 - (d_v/d_c)} but the real rate is {np.size(x)/np.size(y)}")
    print(f"{sucess/m} fraction of packets arrived sucessfully")

    tot_r.append(1 - (d_v/d_c))
    tot_ar.append(sucess/m)
    all_SNR.append(path_loss(d)[1])
    #print(bits_to_float(x)[0])

plt.figure()
plt.plot(all_SNR,tot_ar)
plt.scatter(all_SNR,tot_ar)
plt.xlabel("SNR")
plt.ylabel("Success Rate")
plt.show()

