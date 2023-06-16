import numpy as np
import matplotlib.pyplot as plt
import struct
from scipy import signal
import soundfile as sf

class FSK_Generator():

    def __init__(self):
        self.t = 0
        self.f = 915e6
        self.Fs = 1e7 # sample rate of simulation
        self.bw = 75_000
        self.f_1 = self.f + self.bw
        self.f_0 = self.f - self.bw
        self.sym_size = 40
        self.k = 1000
        self.mu = 1e-3
        self.l = 1
        self.d = 10_000
        
    def generate_packet(self,syms):

        tot = []
        for sym in syms:
            tot.append(self.generate_symbol(sym))

        tot = self.flatten(tot)

        self.l = len(tot)

        return tot

    def generate_symbol(self,sym):
        s = []
        N = self.sym_size 

        if sym == 0:
            step = ((2*np.pi)*self.f_0)/self.Fs
        else:
            step = ((2*np.pi)*self.f_1)/self.Fs

        for i in range(N):
            s.append(complex(np.cos(self.t),np.sin(self.t)))
            self.t += step

        return s

    def flatten(self,l):
        return [item for sublist in l for item in sublist]

    def white_noise(self):
        a = np.random.normal(0,self.mu,self.l)
        b = 1 - a

        return b

    def path_loss(self):

        Lfs_dB = 20*np.log10(self.d) + 20*np.log10(self.f) - 147.55

        print(Lfs_dB)

        return 10**(-1*Lfs_dB/10)
           
    def multipath(self):
        # Simulation Params, feel free to tweak these
        v_mph = 1 # velocity of either TX or RX, in miles per hour
        center_freq = self.f # RF carrier frequency in Hz
        N = 100 # number of sinusoids to sum

        v = v_mph * 0.44704 # convert to m/s
        fd = v*center_freq/3e8 # max Doppler shift
        print("max Doppler shift:", fd)
        t = np.arange(0, ((self.l*self.k)/self.Fs), self.k/self.Fs) # time vector. (start, stop, step)
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

    def demod(self,packet):
        t = np.arange(0, len(packet)/self.Fs, 1/self.Fs)

        plt.figure()
        plt.plot(t,np.real(packet))
        #plt.plot(t,np.imag(packet))


        vco = []
        for i in range(len(packet)):
            vco.append(complex(np.cos(i*(2*np.pi*self.f)/(self.Fs)),np.sin(i*(2*np.pi*self.f)/(self.Fs))))
        convolved = np.array(vco)*packet

        sos = signal.butter(1,0.1*self.Fs, 'lp', fs=self.Fs, output='sos')
        filtered = signal.sosfilt(sos, convolved)

        #Lets make the ring graph thing
        x = []
        y = []
        r = []
        theta = []
        for i in filtered:
            r.append(np.abs(i))
            theta.append(np.angle(i))

            x.append(r[-1]*np.cos(theta[-1]))
            y.append(r[-1]*np.sin(theta[-1]))

        plt.figure()
        plt.scatter(x,y)
        plt.xlabel("Real")
        plt.ylabel("Imaginary")

        angle_diff = -1*(np.angle(filtered[:-1] * np.conj(filtered[1:])))

        plt.figure()
        plt.plot(t[1:],angle_diff)
        plt.xlabel("Time")
        plt.ylabel("Magnitude")

        plt.figure()
        plt.plot(t,np.real(channel))
        plt.plot(t,np.imag(channel))

        # How many elements each
        # list should have
        n = self.sym_size
        x = list(divide_chunks(angle_diff, n))

        bits = []
        for i in x:
            if np.mean(i) > 0:
                bits.append(1)
            else:
                bits.append(0)

        print(f"The BER is {differences(syms,bits)}")
        #print(syms)
        #print(bits)
        print(len(bits))

        plt.show()

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


m = FSK_Generator()

file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
data, sample_rate = sf.read(file)
m.k = 100
m.mu = 1e-9
m.d = 100

result = data[:60]
#result = [0.874]
syms = float_to_bits(result)

packet = m.generate_packet(syms)

channel = m.multipath()
noise = m.white_noise()
path_loss = m.path_loss()
packet = channel*packet*path_loss + noise

m.demod(packet)

