import numpy as np
import matplotlib.pyplot as plt
import math
import struct
import soundfile as sf

def mag(x): 
    m = []
    for i in x:
        m.append(np.abs(i)**2)
    return m

def find_max(x):
    index = 0
    val = 0
    j = 0
    for i in x:
        if i > val:
            index = j
            val = i
        j += 1
    return index

def dechirp_generator(SF,BW):

    m = 0
    two_SF = 2**SF

    pi = 3.14
    f = []
    theta = []
    s_real = []
    s_imag = []

    sym_time = np.linspace(0,Ts/2,int(two_SF))

    #Generate Frequency
    for t in sym_time:
        if t >= 0 and t < (1-(m/two_SF))*Ts:
            f_tmp = BW*(((t/Ts)+(m/two_SF)-0.5))
        elif t >= (1-(m/(two_SF)))*Ts and t < Ts:
            f_tmp = BW*((t/Ts) + (m/(two_SF)-1.5))
        f.append(f_tmp)

    #Generate Phase
    for t in sym_time:
        if t >= 0 and t < (1-(m/two_SF))*Ts:
            p1 = (t**2)/(2*Ts)
            p2 = (m/two_SF)*t
            p3 = -0.5*t
            theta_tmp = 2*pi*BW*(p1 + p2 + p3)
        elif t >= (1-(m/(two_SF)))*Ts and t < Ts:
            p4 = (t**2)/(2*Ts)
            p5 = (m/two_SF)*t
            p6 = -1.5*t
            theta_tmp = 2*pi*BW*(p4 + p5 + p6)
        theta.append(theta_tmp)
        s_real.append(np.cos(theta_tmp))
        s_imag.append(np.sin(theta_tmp))

    s_real = np.array(s_real)
    s_imag = np.array(s_imag)

    return s_real,s_imag


def chirp_generator(SF,BW,m):

    pi = 3.14
    f = []
    theta = []
    s_real = []
    s_imag = []
    two_SF = 2**SF

    sym_time = np.linspace(0,Ts,int(two_SF))

    #Generate Frequency
    for t in sym_time:
        if t >= 0 and t < (1-(m/two_SF))*Ts:
            f_tmp = BW*(((t/Ts)+(m/two_SF)-0.5))
        elif t >= (1-(m/(two_SF)))*Ts and t < Ts:
            f_tmp = BW*((t/Ts) + (m/(two_SF)-1.5))
        f.append(f_tmp)

    #Generate Phase
    for t in sym_time:
        if t >= 0 and t < (1-(m/two_SF))*Ts:
            p1 = (t**2)/(2*Ts)
            p2 = (m/two_SF)*t
            p3 = -0.5*t
            theta_tmp = 2*pi*BW*(p1 + p2 + p3)
        elif t >= (1-(m/(two_SF)))*Ts and t < Ts:
            p4 = (t**2)/(2*Ts)
            p5 = (m/two_SF)*t
            p6 = -1.5*t
            theta_tmp = 2*pi*BW*(p4 + p5 + p6)
        theta.append(theta_tmp)
        s_real.append(np.cos(theta_tmp))
        s_imag.append(np.sin(theta_tmp))

    s_real = np.array(s_real)
    s_imag = np.array(s_imag)

    return s_real,s_imag

def multipath(Ts,l,k):
    # Simulation Params, feel free to tweak these
    v_mph = 1 # velocity of either TX or RX, in miles per hour
    center_freq = 915e6 # RF carrier frequency in Hz
    N = 100 # number of sinusoids to sum


    v = v_mph * 0.44704 # convert to m/s
    fd = v*center_freq/3e8 # max Doppler shift

    t = np.arange(0, k*Ts, (k*Ts)/l) # time vector. (start, stop, step)
    x = np.zeros(len(t))
    y = np.zeros(len(t))
    for i in range(N):
        alpha = (np.random.rand() - 0.5) * 2 * np.pi
        phi = (np.random.rand() - 0.5) * 2 * np.pi
        x = x + np.random.randn() * np.cos(2 * np.pi * fd * t * np.cos(alpha) + phi)
        y = y + np.random.randn() * np.sin(2 * np.pi * fd * t * np.cos(alpha) + phi)

    # z is the complex coefficient representing channel, you can think of this as a phase shift and magnitude scale
    z = (1/np.sqrt(N)) * (x + 1j*y) # this is what you would actually use when simulating the channel
    z_mag = np.abs(z) # take magnitude for the sake of plotting
    z_mag_dB = 10*np.log10(z_mag) # convert to dB

    return z

def white_noise(mu,l):
    a = np.random.normal(0,mu,l)
    b = 1 - a

    return b


def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

def float_to_bits(result):
    bit_string = ""
    bit_array = []
    for i in result:
        tmp = binary(i)
        bit_string += tmp
        for j in tmp:
            bit_array.append(int(j))

    return bit_array

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def differences(a,b):
    temp3 = []
    for i in range(len(a)):
        if int(a[i]) != int(b[i]):
            temp3.append(i)
    return (len(temp3)/len(a))



SF = 4
BW = 250e3
Ts = (2**SF)/BW
two_SF = 2**SF
theta_0 = 0
m = 0
out = []
mu = 1e-9

file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
data, sample_rate = sf.read(file)
result = data[:60]

a = float_to_bits(result)
b = list(divide_chunks(a,SF))

test_symbols = []
for i in b:
    c = int("".join(str(x) for x in i), 2)
    test_symbols.append(c)


#test_symbols = np.linspace(0,two_SF-1,two_SF)

for m in test_symbols:
    m = int(m)
    [s_r,s_i] = chirp_generator(SF,BW,m)

    k = 1
    channel = np.array(multipath(Ts,len(s_r),k))
    noise = white_noise(mu,len(s_r))

    #s_r = s_r * np.real(channel) * np.real(noise)
    #s_i = s_i * np.imag(channel) * np.real(noise)

    tmp_max = 0
    plt_sp = []

    for n in range(two_SF):
        [d_r,d_i] = chirp_generator(SF,BW,n)

        t_r = s_r*d_r + s_i*d_i
        t_i = s_i*d_r - s_r*d_i

        tmp = []
        for i in range(len(t_r)):
            tmp.append(complex(t_r[i],t_i[i]))
        t_r = tmp

        #Post signal generation
        sp = mag(np.fft.fft(t_r,int(two_SF)))
        plt_sp = sp

        v_max = np.amax(sp)
        if v_max > tmp_max:
            tmp_max = v_max
            sym_max = n

    out.append(sym_max)

    print(f"The symbol number is {m} and the out is {out[-1]}")


diff = differences(out,test_symbols)
print(f"The BER is: {diff}")

plt.figure()
plt.plot(out)
plt.plot(test_symbols)
plt.show()


