import numpy as np
import matplotlib.pyplot as plt
import struct
from scipy import signal
from codecs import decode
import ctypes
from reedsolo import RSCodec
import soundfile as sf


class test:
    def __init__(self):
        self.msg = 0
        self.x = 0
        self.y = 0

class FSK_Generator():

    def __init__(self):
        self.t = 0
        self.f = 915e6
        self.bw = 75_000
        self.Fs = 1e7 # sample rate of simulation
        self.f_1 = self.f + self.bw
        self.f_0 = self.f - self.bw
        self.sym_size = 40
        self.mu = 1e-14

        self.Gt = 0
        self.Gr = 0

    def generate_packet(self,nums,d):

        #syms = self.float_to_bits(nums)
        syms = nums

        tot = []
        for sym in syms:
            tot.append(self.generate_symbol(sym))

        tot = self.flatten(tot)

        self.l = len(tot)

        fspl = self.path_loss(d)

        return np.array(tot)*fspl

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


    def path_loss(self,d,dB = False):

        Lfs_dB = 20*np.log10(d) + 20*np.log10(self.f) - 147.55 + self.Gt + self.Gr

        if dB == False:
            return 10**(-1*Lfs_dB/10)
        else:
            return int(Lfs_dB)

    def float_to_bits(self,result):
        bit_string = ""
        bit_array = []
        for i in result:
            tmp = self.binary(i)
            bit_string += tmp
            for j in tmp:
                bit_array.append(int(j))

        return bit_array

    def binary(self,num):
        return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

    def white_noise(self,l):
        kB = 1.38e-23
        T = 290
        Pn = kB*T*self.bw
        a = np.random.normal(loc=0,scale=Pn,size=l)*1000

        return a

    def generate_packet_mp_d(self,float_num,d,n):
        los = self.generate_packet(float_num,d) 
        los = np.add(los,self.white_noise(len(los)))

        comb = np.array(los)
        dists = np.linspace(d,1.25*d)
        for dis in dists:
            path_len = dis
            delay = ((path_len - d)/(3e8))*self.Fs
            
            samp_delay = int(delay)

            tmp = self.generate_packet(float_num,path_len)
            pad = np.zeros(samp_delay)

            tmp_path = np.append(pad,tmp[:len(tmp) - samp_delay])
            comb = np.add(comb,tmp_path) + self.white_noise(len(comb))
                                        
        return los,comb

    def generate_packet_mp(self,float_num,d,n):
        los = self.generate_packet(float_num,d) 
        los = np.add(los,self.white_noise(len(los)))

        comb = np.array(los)
        for i in range(n):
            path_len = np.random.rand()*d*0.25 + d
            delay = ((path_len - d)/(3e8))*self.Fs
            
            samp_delay = int(delay)

            tmp = self.generate_packet(float_num,path_len)
            pad = np.zeros(samp_delay)

            tmp_path = np.append(pad,tmp[:len(tmp) - samp_delay])
            comb = np.add(comb,tmp_path) + self.white_noise(len(comb))
                                        
        return los,comb

    def demod(self,packet,plot = False):
        t = np.arange(0, len(packet)/self.Fs, 1/self.Fs)

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
            
        angle_diff = -1*(np.angle(filtered[:-1] * np.conj(filtered[1:])))

        if plot == True:

            plt.figure()
            plt.scatter(x[100:],y[100:])
            plt.xlabel("Real")
            plt.ylabel("Imag")

            plt.figure()
            plt.plot(angle_diff[100:3000])
            plt.xlabel("Time")
            plt.ylabel("Magnitude")
            plt.title("Recovered Bits")


        # How many elements each
        # list should have
        n = self.sym_size
        x = list(self.divide_chunks(angle_diff, n))

        bits = []
        for i in x:
            if i[int(self.sym_size/2)] > 0:
                bits.append(1)
            else:
                bits.append(0)

        return bits

    def divide_chunks(self,l, n):
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def differences(self,a,b):
        temp3 = []
        for i in range(len(a)):
            if int(a[i]) != int(b[i]):
                temp3.append(i)
        return (len(temp3)/len(a))

    def bitstring_to_bytes(self,s):
        v = int(s, 2)
        b = bytearray()
        while v:
            b.append(v & 0xff)
            v >>= 8
        return bytes(b[::-1])

    def float_to_bit_array(self,float_num,rsc,encode=True):
        buf = struct.pack('%sf' % len(float_num), *float_num)

        if encode == True:
            encoded = rsc.encode(bytearray(buf))
        else:
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

    def demod_to_float(self,bits,rsc,encode=True):
        bit_str = ""
        for i in bits:
            bit_str += str(i)
        tmp = self.bitstring_to_bytes(bit_str)

        if encode == True:
            decoded,decoed_ecc,errata_pos = rsc.decode(tmp)
            #print(f"There are: {len(list(errata_pos))} errors")
        else:
            decoded = tmp

        chunks = self.divide_chunks(decoded,4)
        decoded_float = []
        for i in chunks:
            decoded_float.append(float(struct.unpack('f', i)[0]))

        return decoded_float


    def calc_dBm(self,sig):
        T = len(sig)/self.Fs
        mW = 1e-3

        power = 0 

        for i in sig:
            power += i**2

        power = (1/T)*power
        dBm = 10*np.log10(power/mW)

        return np.real(dBm)