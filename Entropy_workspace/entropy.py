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

    p_zero = float(ones)/len(a)
    p_one = 1 - p_zero
    return -1*(p_zero*np.log2(p_zero) + p_one*np.log2(p_one))
    
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



range_thresh = np.linspace(0.1,0.9,100)
sizes = [1920]


for size in sizes:

    compress_val = []
    tot_entropy = []
    tot_post_compress = []

    for thresh in range_thresh:

        array = array_random(thresh,int(size))

        #file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
        #data, sample_rate = sf.read(file)
        #array = data[:60]

        tot_entropy.append(calc_prob_float(array))

        result = fpzip.compress(array,precision=24, order='F')
        compressed = result
        tot_post_compress.append(calc_prob_byte(result))

        tmp_result = fpzip.decompress(result, order='F') 
        result = tmp_result.flatten()

        len_orig = float(len(bytearray(array)))
        len_compress = float(len(bytearray(compressed)))

        compress_val.append(len_orig/len_compress)

    plt.figure(1)
    plt.scatter(tot_entropy,compress_val,label="Compression Ratio of Packet")
    plt.plot(tot_entropy,compress_val)
    plt.ylim([0, 10])
    plt.xlabel("Entropy of Original Packet")
    plt.ylabel("Compression Ratio/Entropy of Compressed Packet")

    #plt.figure(2)
    plt.scatter(tot_entropy,tot_post_compress,label="Entropy of Compressed packet")
    plt.plot(tot_entropy,tot_post_compress)
    #plt.xlabel("Entropy of Original Packet")
    #plt.ylabel("Entropy of Compressed Packet")
    #plt.ylim([0, 2])
    plt.legend()


plt.savefig('myimage.svg', format='svg', dpi=1200)

file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
data, sample_rate = sf.read(file)
print(f"Entropy of Audio File {calc_prob_float(data)}")

plt.show()


