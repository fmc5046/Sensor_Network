import numpy as np
import matplotlib.pyplot as plt
import struct
from scipy import signal
from codecs import decode
import ctypes
from reedsolo import RSCodec
import soundfile as sf

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


    def path_loss(self,d):

        Lfs_dB = 20*np.log10(d) + 20*np.log10(self.f) - 147.55 + self.Gt + self.Gr
        return 10**(-1*Lfs_dB/10)

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
        tmp = a.bitstring_to_bytes(bit_str)

        if encode == True:
            decoded,decoed_ecc,errata_pos = rsc.decode(tmp)
            #print(f"There are: {len(list(errata_pos))} errors")
        else:
            decoded = tmp

        chunks = a.divide_chunks(decoded,4)
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


#Get data
file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
data, sample_rate = sf.read(file)
result = data[:60]


#Parameters
d = 6500 #Distance Transmitted
n = 30 #Number of multipaths added

rec = 0
tot = 20
#Do it many times for test purposes for each ECC value
#fec_ECC = [0,10,40] #Error Correction Codes
fec_ECC = [0]

#dists = [2000,3500,5000,6500,8000]
dists = [1,1.25,1.5,1.75,2]
d = 1000

pack_suc = []
pow_diff = []

for k in dists:
    for ecc in fec_ECC:

        if ecc == 0:
            encode = False
        else:
            encode = True

        rec = 0

        for _ in range(tot):

            #Initialize
            rsc = RSCodec(ecc)  #Reed Solomon Encoder
            a = FSK_Generator() #FSK mod/demod

            #Generate Original Bit array and encode with RSC
            float_num = np.random.rand(60)
            og_nums = float_num
            bit_array = a.float_to_bit_array(float_num,rsc,encode=encode)

            #Generate waveform with noise and multipath
            los1,comb1 = a.generate_packet_mp_d(bit_array,d,n)

            x1 = a.calc_dBm(comb1)
            #print(f"The far one {x1}")

            #Generate Original Bit array and encode with RSC
            float_num = np.random.rand(60)
            bit_array = a.float_to_bit_array(float_num,rsc,encode=encode)

            #Generate waveform with noise and multipath
            los2,comb2 = a.generate_packet_mp_d(bit_array,k*d,n)

            x2 = a.calc_dBm(comb2)
            #print(f"The close one {x2}")

            print(f"The difference is {x2 - x1}")
            pow_diff.append(x2 - x1)

            #Combine the two packets due to a collision
            comb = np.add(comb1,comb2)

            #Demoduate and recover
            bits = a.demod(comb,plot=False)

            #Decode the bits with RSC
            try:
                decoded_float = a.demod_to_float(bits,rsc,encode=encode)

                #For BER calc
                bits_orig = a.float_to_bits(og_nums)
                recovered_bits = a.float_to_bits(decoded_float)
                #print(f"BER: {a.differences(bits_orig,recovered_bits)}")

                #plt.figure()
                #plt.plot(float_num)
                #plt.plot(decoded_float)

                if a.differences(bits_orig,recovered_bits) < 1e-6:
                    rec += 1
                    pack_suc.append(1)
                else:
                    pack_suc.append(0)
            except:
                message = 5
                pack_suc.append(0)

        print(f"Recived {rec} and Sent {tot} for distance {d} and encode {encode} and ECC is {ecc}")


plt.figure()
for i in range(len(pow_diff)):
    if int(pack_suc[i]) == int(1):
        plt.scatter(i,pow_diff[i],c='blue')
    else:
        plt.scatter(i,pow_diff[i],c='red')
plt.show()




    
