from sqlite3 import Timestamp
import soundfile as sf
import numpy as np
import compress
import datetime
from reedsolo import RSCodec, ReedSolomonError
import random
import struct
import math
from skopt import Optimizer
import time     


class dataBuffer():

    def __init__(self,value,timestamp,constraint = "distortion"):
        self.value = value
        self.constaraint = constraint
        self.timestamp = timestamp

class posSensor():

    def __init__(self,time):
        self.value = 0
        self.timestamp = time

class classSensor():

    def __init__(self,time):
        self.value = []
        self.timestamp = time

class Node:
    def __init__(self,id,sensor_type = 'audio'):

        #Sim time
        self.sim_time = 0

        #General
        self.id = id
        self.rx_buffer = []
        self.tx_buffer = []
        self.class_data_buffer = []
        self.control_data_buffer = []
        self.class_sensor = classSensor(self.sim_time)
        self.pos_sensor = posSensor(self.sim_time)
        self.sensor_type = sensor_type

        #For generate data and generate packet
        self.added_per_loop = 4410
        self.scheduler_type = 'g'  # (p)eriodic or (g)reedy or (d)rift plus penalty
        self.tau = 0.4

        self.tmp_data = []
        self.file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
        #self.file = "/home/fred/Lingua_Franca/Playground/small.wav"
        self.size = 220*10
        self.precision = 12
        self.data_sqn = 0
        self.max_size = 220
        self.offset = 30

        #Set up Reed Solomon ECC
        self.ecc_sym = 10 #or 10
        self.rsc = RSCodec(self.ecc_sym)  # ecc symbols

        #For process data
        self.application_data = []

        #For data scheduling
        self.count = 0

        self.aoi_class = []
        self.class_t = []

        self.aoi_control = []
        self.control_t = []
        self.last_send = self.sim_time

        self.tmp_aoi_c = [1] * 10
        self.tmp_aoi_nn = [1] * 10

        self.number_of_packets = 0
        self.ACK_got = 0
        self.average = 0.0

        #For Lyampunov Scheduling
        self.V = 1
        self.a = 1

        #For sensor
        self.real_class_sensor = True

        #For value selector for greedy
        self.bit_precision = [32,24,18,14]
        self.choices = [14,10000]

        self.all_choices = []
        self.all_len_values = []

        self.len_measurements =[]

        self.thresh = 100
        self.thresh2 = 35
        self.thresh3 = 14

        #For Bayes Opt
        self.optimizer = []
        self.new_try_thresh = 200

        self.done = False

        #For reciver
        self.tot_array = bytearray(b'')
        self.last_index = 0

        #For testing results
        self.total_packet = 0
        self.packet_success = 0

        #For basic OS
        self.p1_count = 0
        self.p2_count = 0

        #For ACK mechanism
        self.got_ACK = True
        self.tmp_message = b''

    def recive(self,read_serial):
        #print(read_serial)
        #This is to clean up and use the serial data to get back to the orginal data
        a = str(read_serial)
        a = a[2:len(a)-5]

        list_of_words = a.split()
        s = ''

        #Remove extra 255's from end of list
        first_last = 1000
        for i in range(len(list_of_words)):
            if list_of_words[len(list_of_words) - i - 1] != '255' and list_of_words[len(list_of_words) - i - 1] != '0':
                first_last = len(list_of_words) - i
                break

        list_of_words = list_of_words[:first_last]
        index = int(list_of_words[-1])
        list_of_words = list_of_words[:len(list_of_words)-1]

        #Trim the 4th packet of extra 00's and ff's
        if index == 4:
            first_last = 1000
            for i in range(len(list_of_words)):
                if list_of_words[len(list_of_words) - i - 1] != '255' and list_of_words[len(list_of_words) - i - 1] != '0':
                    first_last = len(list_of_words) - i
                    list_of_words = list_of_words[:first_last]
                    break
        
        if index == 1:
            self.last_index = 1
            self.tot_array = bytearray(b'')
            tot = b''
            for i in list_of_words:
                tmp = int(i).to_bytes(1,'big')
                tot = tot + tmp
            recived = bytearray(tot)
            self.tot_array = self.tot_array + recived

        if(index == 2 and self.last_index == 1):
            self.last_index = 2
            tot = b''
            for i in list_of_words:
                tmp = int(i).to_bytes(1,'big')
                tot = tot + tmp
            recived = bytearray(tot)
            self.tot_array = self.tot_array + recived

        if(index == 3 and self.last_index == 2):
            self.last_index = 3
            tot = b''
            for i in list_of_words:
                tmp = int(i).to_bytes(1,'big')
                tot = tot + tmp
            recived = bytearray(tot)
            self.tot_array = self.tot_array + recived

        if(index == 4 and self.last_index == 3):
            tot = b''
            for i in list_of_words:
                tmp = int(i).to_bytes(1,'big')
                tot = tot + tmp
            recived = bytearray(tot)
            self.tot_array = self.tot_array + recived


        #Add recived packet after its been converted
        if len(self.tot_array) > 180:
            self.recive_data(self.tot_array)
            self.tot_array = bytearray(b'')

    def send(self,transmit):
        val = []
        if transmit != 0:
            for i in transmit:
                val.append(i)

        return val


    #Generate data#Generate data
    def generate_data(self):

        if self.real_class_sensor == False:
            #For the hydrophone data
            #If the buffer is empty add new file
            if len(self.tmp_data) < 1:
                data, sample_rate = sf.read(self.file)
                self.tmp_data = list(data)

            #Transfer over some samples from tmp_data to actual buffer (for real data the tmp buffer would be the actual sensor)
            #Currently pulling data from file, change for streaming from a sensor
            #This is extreamly slow, speed up!!!!!!!
            if len(self.tmp_data) > self.added_per_loop:
                timestamp = self.sim_time
                
                for i in range(self.added_per_loop):
                    self.class_data_buffer.append(dataBuffer(self.tmp_data.pop(0),timestamp=timestamp))

            else:
                print("No more data!")
                self.done = True


        else:
            #For the classifier sensor (real one)
            a = self.class_sensor.value
            timestamp = self.sim_time
            
            #print(type(a))
            #print(f"The class buffer has {len(self.class_data_buffer)} data left")
            if type(a) is list:
                for i in a:
                    self.class_data_buffer.append(dataBuffer(i,timestamp=timestamp))
            else:
                self.class_data_buffer.append(dataBuffer(a,timestamp=timestamp))

        #For the pendulum sensor data move one data from tmp to data as it is added elsewhere
        self.control_data_buffer.append(dataBuffer(self.pos_sensor.value,self.pos_sensor.timestamp))

    #This is where I generate a packet, the size of the packet depends on the type of data
    #Move some of this to the compress library (and rename it to something better)
    def generate_compressed_packet(self):

        #Here is the greedy len control 
        #self.precision = self.greedy_len_control(self.class_data_buffer)
        #self.precision = self.threshold_control(self.class_data_buffer)
        
        done = False

        if self.precision >= 18:
            self.offset = 30
        else:
            self.offset = 10

        while(done == False and len(self.class_data_buffer) > 10):
            
            data = ''

            tmp = np.empty(1)
            time_stamp = self.class_data_buffer[0].timestamp

            if len(self.class_data_buffer) >= self.size:
                for i in range(self.size):
                    tmp = np.append(tmp,self.class_data_buffer[i].value)
            else:
                break

            #Now compress and encode
            data = compress.compress_encode_packet(tmp,self.precision,time_stamp,self.data_sqn,self.rsc)

            #Measure File size
            file_size = len(bytes(data))

            #Calculate Error
            size_error = int((self.max_size - file_size)*1)
            #print(f"The size is {self.size} and the max size is {self.max_size} and the file size is {file_size} and the offset is {self.offset} and error is {size_error}")

            #Check what action should be taken
            #Too big make size smaller
            if  file_size > self.max_size:
                self.size += size_error

            #Too small make size bigger
            elif file_size < self.max_size - self.offset:
                self.size += size_error

                if len(self.class_data_buffer) < self.size:
                    #done = True
                    break

            #Good size send it
            else:
                done = True

                #Roll over sqn
                if self.data_sqn > 250:
                    self.data_sqn = 0
                else:
                    self.data_sqn += 1

                #Send data
                if len(data) > 1:
                    self.tx_buffer.append(data)

                    #For ACK mechanism
                    self.tmp_message = data
                    self.got_ACK = False
                    
                    #For AoI measurements
                    self.aoi_class.append(self.sim_time - time_stamp)
                    self.class_t.append(self.sim_time)

                    #For short term AoI measure
                    self.tmp_aoi_nn.pop(0)
                    self.tmp_aoi_nn.append(self.aoi_class[-1]/1_000_000_000)

                    #And remove the old data
                    if len(self.class_data_buffer) <= self.size:
                        self.class_data_buffer = []
                    else:
                        for i in range(self.size):
                            self.class_data_buffer.pop(0)
                break

    def generate_uncompressed_packet(self):
        if len(self.control_data_buffer) >= 1:

            data = self.control_data_buffer.pop(-1)
            self.tx_buffer.append(data.value)

            #For AoI measurements plotting
            self.aoi_control.append(self.sim_time - self.last_send)
            self.last_send = self.sim_time
            self.control_t.append(self.sim_time)

            #For short term AoI measure
            self.tmp_aoi_c.pop(0)
            self.tmp_aoi_c.append(self.aoi_control[-1]/1_000_000_000)

            #Remove all old data
            self.control_data_buffer = []

    def periodic_scheduler(self):
        if self.count >= 3:
            self.count = 0
            return 1
        else:
            self.count += 1
            return 0

    def greedy_scheduler(self):
        #self.tau = 0.3
        if (self.sim_time - self.last_send)/1_000_000_000 > self.tau:
            return 1
        else:
            return 0         

    def drift_plus_penalty(self):
        Q = [len(self.class_data_buffer), len(self.control_data_buffer)]

        #Calculate L
        L = 0
        #for i in range(len(Q)):
        #    L += 0.5*Q[i]**2

        #Calculate Drift plus Penalty for sending control data
        #Estimate L + 1
        L_1 = L - 1
        p = self.penalty(0) #Penalty for AoI of control
        delta_control = L_1 - L

        #Calculate DPP for class data
        #Estimate L + 1
        delta = self.greedy_len_control(self.class_data_buffer,output='delta')
        L_1 = L - delta
        p = self.penalty((self.sim_time - self.last_send)/1_000_000_000) #Penalty for AoI of control
        delta_class = L_1 - L + self.V*p

        #print(f"The delta control is {delta_control:0.2f} and the delta class is {delta_class:0.2f} and the penalty is {p:0.2f}")

        #Select sending the packet that reduces the score the most
        if delta_control < delta_class:
            return 1
        else:
            return 0
  
    #Exponential penalty 
    def penalty(self,aoi):
        p = (math.exp(12*aoi)) - 1
        return p

    def init_optimizer(self):
        acq_func_kwargs = {"kappa": 10000}
        optimizer = Optimizer(
        dimensions=[(1,10000),(1,10000),(1,10000)],
        base_estimator='rf',
        n_initial_points=200,
        initial_point_generator="grid",
        acq_func= "gp_hedge",
        acq_func_kwargs=acq_func_kwargs
        )

        self.optimizer = optimizer

    def pick_new_choices_bayes(self):
        if self.number_of_packets >= self.new_try_thresh:
            done = False

            while(done == False):
                print("Try new values--------------------")
                print(f"The current len of the buffer is {len(self.class_data_buffer)}")
                a = self.thresh
                print(f"With values {a}")

                self.all_choices.append(a)
                self.all_len_values.append(np.mean(self.len_measurements))

                #And pick new values from optimizer
                x = [self.thresh,self.thresh2,self.thresh3]
                y = np.mean(self.len_measurements)
                print(x)
                print(y)
                self.optimizer.tell(x,y)
                new = self.optimizer.ask()
                print(new)
                self.thresh = new[0]
                self.thresh2 = new[1]
                self.thresh3 = new[2]


                if self.thresh > self.thresh2 and self.thresh > self.thresh3 and self.thresh2 > self.thresh3:
                    #Reset test by clearing out the data buffers and number of packets sent
                    #self.class_data_buffer = []
                    self.number_of_packets = 0
                    self.ACK_got = 0
                    self.len_measurements = []
                    done = True
                else:
                    self.len_measurements = [999999]

    def pick_new_choices_rand(self):
        if self.number_of_packets >= 500:
            print("Try new values--------------------")
            print(f"The current len of the buffer is {len(self.class_data_buffer)}")
            a = self.thresh
            print(f"With values {a}")

            self.all_choices.append(a)
            self.all_len_values.append(np.mean(self.len_measurements))

            #Reset test by clearing out the data buffers and number of packets sent
            #self.class_data_buffer = []
            self.number_of_packets = 0
            self.len_measurements = []

            #And pick new random values
            self.thresh = random.randint(1,20000)

    def threshold_control(self,buf):
        if len(buf) > self.thresh:
            precision = self.bit_precision[3]
        elif len(buf) > self.thresh2:
            precision = self.bit_precision[2]
        elif len(buf) > self.thresh3:
            precision = self.bit_precision[1]
        else:
            precision = self.bit_precision[0]
        return precision


    def greedy_len_control(self,buf,output = 'precision'):

        best = self.choices[0]
        for i in self.choices:
            if len(buf) > i and i > best:
                best = i
        
        precision = self.bit_precision[-1]
        precision_index = self.choices.index(best)
        precision = self.bit_precision[precision_index]

        if output == 'precision':
            return precision
        else:
            return best

    def scheduler(self,mode):
        if mode == 'p':
            return self.periodic_scheduler()
        elif mode == 'g':
            return self.greedy_scheduler()
        elif mode == 'd':
            return self.drift_plus_penalty()
        else:
            return 0

    #This is where I generate a packet, either compressed or not compressed based on the sensor data type
    def generate_packet(self):

        if self.scheduler(self.scheduler_type):
            self.generate_uncompressed_packet()
        else:
            if self.got_ACK == True:
                self.generate_compressed_packet()
            else:
                self.tx_buffer.append(self.tmp_message)

    #Transmit value
    def transmit_data(self):
        if len(self.tx_buffer) > 1:
            transmit = self.tx_buffer.pop(0)
            self.len_measurements.append(len(self.class_data_buffer))
            return transmit
        else:
            return 0

    #Add data to rx buffer
    def recive_data(self,recived_message):
        self.rx_buffer.append(recived_message)

    #Process whats in the RX buffer
    def process_recived(self):
        app_data = [0]
        if self.id == 1 and len(self.rx_buffer) > 1:

            #Based on sensor type pick where the data comes from 
            tmp = self.rx_buffer.pop(0)

            #Check the type, if its a list  or byte array treat differently
            if type(tmp) == bytearray:

                rec = compress.decompress_packet(tmp,self.ecc_sym)
                #Now add the recived data to the application buffer for further use 
                #If it is long enough for a classification then output it (this should probably be moved to the app side)
                self.total_packet += 1
                if len(rec) > 1:
                    #Log success and send ACK
                    self.packet_success += 1
                    self.tx_buffer.append([124,156,143])


                    #Append to application data
                    for samp in rec:
                        self.application_data.append(samp)

                print(f"Packet Success Rate is {(self.packet_success/self.total_packet):.2f} with {self.total_packet}")
                #print(f"The app data len is {len(self.application_data)}")
                amount = 1800*100
                if len(self.application_data) >= int(amount) or self.total_packet >= 95:
                    app_data = self.application_data[:amount]
                    self.application_data = self.application_data[amount:]
                    
            if(type(tmp) == list):
                app_data = tmp

        return app_data


    #Main loop outputs message for transmission or for physical use (i.e. sensor data for classifier ect...)
    def run(self):
        
        if self.id == 0 and self.p1_count > 5:
            self.generate_data()
            self.generate_packet()
            self.p1_count = 0
        self.p1_count += 1
            
        transmit = self.transmit_data()
        use = self.process_recived()
        out = [transmit,use]

        #Check to see if use new gains
        self.pick_new_choices_bayes()
        
        return out
    
        
