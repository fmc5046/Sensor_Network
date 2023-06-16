from cProfile import label
from bson import encode
import numpy as np
from reedsolo import RSCodec, ReedSolomonError
import struct
import matplotlib.pyplot as plt
import math
from scipy import special as sp
from scipy.stats import binom
from scipy.special import lambertw



def qfunc(x):
    return 0.5-0.5*sp.erf(x/np.sqrt(2))

def sim_channel(data_in,BER):

    error_percent = 1/max(BER,1e-10)

    data_out = []
    for i in range(len(data_in)):
        b_out = ""
        
        b_in = bin(data_in[i])
        for j in range(len(b_in)-2):
            r = np.random.randint(error_percent)
            if(r == 0):
                if b_in[j+2] == 0:
                    b_out = b_out + "1"
                else:
                    b_out = b_out + "0"
            else:
                b_out = b_out + b_in[j+2]
        b_out = int(b_out,2)
        data_out.append(b_out)
    return bytearray(data_out)

def path_loss(d):

    f = 915e6

    Lfs_dB = (20*np.log10(d) + 20*np.log10(f) - 147.55)
    Lfs = 10**(Lfs_dB/10)

    Pr = 1/max(Lfs,1e-30)

    N0_dBm = -101
    N0_dB = N0_dBm
    N0 = 10**(N0_dB/10)

    SNR = Pr/N0

    #For LoRa
    #BER = Pb_AWGN(SNR)

    #For BPSK
    BER = 0.5*math.erfc(np.sqrt(SNR))

    return BER,SNR

def Pb_Ray(SNR):
    SF = 7
    T = 10**(SNR/10)
    H = 5.433
    two_SF = 2**SF

    a =  qfunc(-1*np.sqrt(2*H))
    b = np.sqrt((two_SF*T)/(two_SF*T + 1))
    
    top = (2*H)/(2*(two_SF*T + 1))
    c = np.e**(-1*top)

    d = np.sqrt((two_SF*T + 1)/(two_SF*T))
    e = -1*np.sqrt(2*H) + (np.sqrt(2*H)/(two_SF*T + 1))

    Pb = (a - b*c * qfunc(d * e))

    return Pb

def Pb_AWGN(SNR):

    SF = 7
    two_SF = 2**(SF+1)
    T = 10**(SNR/10)

    a = (T*two_SF)**0.5
    b = (1.386*SF + 1.154)**0.5

    return qfunc(a - b)

def encode_msg(tmp_msg,ecc_sym):
    byte_msg = bytearray()
    for i in tmp_msg:
        ba = bytearray(struct.pack("f", i))  
        byte_msg = byte_msg + ba

    if ecc_sym != 0:
        encoded_msg = rsc.encode(byte_msg)
    else:
        encoded_msg = byte_msg

    return encoded_msg

def decode_msg(channel_msg,ecc_sym):

    if ecc_sym != 0:
        decoded_msg = rsc.decode(channel_msg)[0]
    else:
        decoded_msg = channel_msg

    n = 4
    chunks = [decoded_msg[i:i+n] for i in range(0, len(decoded_msg), n)]

    recovered_msg = []
    for ch in chunks:
        recovered_msg.append((struct.unpack('f', ch))[0])

    return recovered_msg

def check_values(recovered_msg):
    no_match = False
    for i in recovered_msg:
        if int(i) != int(1):
            no_match = True
            break

    return no_match

#Start of the program
if __name__ == "__main__":

    #For changing range
    #ds = np.linspace(1_000,1_500,5)  
    ds = range(1000,1300,50)
    #d = 1_500

    #For changing arrival rate
    mus = np.linspace(10,50,5)
    mu = 75

    errors = [0,20,40,80]
    errors = [0]

    plt.figure()

    all_a = []

    for err in errors:

        all_que = []
        all_tot_val = []
        all_SNR = []
        all_aoi = []
        all_prob = []
        all_theo_aoi = []

        for d in ds:

            tx_buffer = []
            tx_buffer_size_hist = []
            aoi = []

            ecc_sym = err
            if ecc_sym != 0:
                rsc = RSCodec(ecc_sym)  # ecc symbols

            count = 0
            a = 0
            data_sent = 0
            packet_size = 200
            
            while(count < 1000):

                #First add sample to buffer
                tx_buffer.extend([1.34]*int(mu))

                #Calculate how many samples to pull out to fit packet of 200 bytes
                space_left = packet_size - ecc_sym
                stop_index = int(np.floor(space_left/4)) 
                #stop_index = 50
        
                #If buffer is large enough
                if len(tx_buffer) > stop_index:

                    #Pull out sample
                    tmp_msg = tx_buffer[0:stop_index]  #Pull out msg

                    #Then encode
                    encoded_msg = encode_msg(tmp_msg,ecc_sym)

                    #Send over channel
                    channel_msg = sim_channel(encoded_msg,path_loss(d)[0])

                    #Decode
                    try:
                        #Decode the message
                        recovered_msg = decode_msg(channel_msg,ecc_sym)

                        #Check if message has errors
                        no_match = check_values(recovered_msg)

                        if no_match == False:
                            #If it decodes sucessfully then remove top item off the queue
                            tx_buffer = tx_buffer[stop_index:]
                            data_sent += stop_index
                        else:
                            a += 1

                    except:
                        a += 1

                tx_buffer_size_hist.append(len(tx_buffer))
                aoi.append(count - int(data_sent/mu))            
                count += 1

            #plt.plot(tx_buffer_size_hist,label="ECC:" + str(ecc_sym) + " R:" + str((200 - ecc_sym)/200))
            print(f"For ECC {ecc_sym}, {a} messages failed and an index of {stop_index} and message size of {len(encoded_msg)} and a total of {data_sent} values were sent and at distance {int(d)} and buffer size is {len(tx_buffer)} with SNR: {int(path_loss(d)[1])}")
            print(f"Coding rate of {packet_size/(packet_size + ecc_sym)} and AoI of {np.mean(aoi)}")
            all_a.append(a)
            all_SNR.append(path_loss(d)[1])
            all_aoi.append(np.mean(aoi))
            all_prob.append(binom.cdf(0, 200*8,path_loss(d)[0]))

            #all_que.append(len(tx_buffer))
            all_que.append(np.mean(tx_buffer_size_hist))
            all_tot_val.append(data_sent)

            lam = 0.4
            muu = all_prob[-1]
            print(muu)
            print(d)
            p = lam/muu
            y = -1*p*lambertw((-1/p)*np.e**(-1/p))
            o_delta = (1/(2*muu))*(1 + (1/(1 - y)))
            all_theo_aoi.append(abs(o_delta) * 10 + 160)

        plt.plot(all_prob,all_aoi,label= "Sim AoI")
        plt.scatter(all_prob,all_aoi)

        print(all_prob,all_theo_aoi)
        plt.plot(all_prob,all_theo_aoi,label= "Theory DM1 AoI")

    plt.xlabel("Pa")
    plt.ylabel("Average AoI")
    plt.legend()
    plt.show()
        
