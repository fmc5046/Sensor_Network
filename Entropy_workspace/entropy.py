import fpzip
import numpy as np
import soundfile as sf
import struct
import random
import matplotlib.pyplot as plt

def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

def calc_prob_float(result):
    bit_string = ""
    for i in result:
        tmp = binary(i)
        bit_string += tmp

    ones = 0
    zeros = 0
    for i in bit_string:
        if i == "1":
            ones += 1
        else:
            zeros += 1
        
    
    #print(f"Uncompressed % that are ones {float(ones)/len(bit_string)}")
    #print(float(zeros)/len(bit_string))
    p_zero = float(ones)/len(bit_string)
    p_one = 1 - p_zero
    return -1*(p_zero*np.log2(p_zero) + p_one*np.log2(p_one))
    #return p_zero

def calc_prob_byte(result):
    a = bin(int.from_bytes(result, byteorder="big")).strip('0b')

    ones = 0
    zeros = 0
    for i in a:
        if i == "1":
            ones += 1
        else:
            zeros += 1
    
    #print(f"Compressed % that are ones: {float(ones)/len(a)}")
    #print(float(zeros)/len(a))

def array_random(thresh,size):
    x = []
    for j in range(size):
        #x.append(random.random())
        #x.append(0.0)
        if random.random() > thresh:
            x.append(random.random())
        else:
            x.append(0.0)

    return np.array(x)



range_thresh = np.linspace(0,1,100)
sizes = [100,400,1000,10000]

plt.figure()
for size in sizes:

    compress_val = []
    tot_entropy = []

    for thresh in range_thresh:

        array = array_random(thresh,int(size))
        tot_entropy.append(calc_prob_float(array))

        result = fpzip.compress(array,precision=32, order='F')
        compressed = result
        calc_prob_byte(result)

        tmp_result = fpzip.decompress(result, order='F') 
        result = tmp_result.flatten()

        len_orig = float(len(bytearray(array)))
        len_compress = float(len(bytearray(compressed)))

        compress_val.append(len_orig/len_compress)

    plt.scatter(tot_entropy,compress_val,label="Original length: " + str(size))
    plt.plot(tot_entropy,compress_val)


file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
data, sample_rate = sf.read(file)
print(f"Entropy of Audio File {calc_prob_float(data)}")

plt.legend()
plt.xlabel("Entropy of Original Packet")
plt.ylabel("Compression Ratio")
plt.show()
