import os
import sys
sys.path.append(os.path.dirname(__file__))
# List imported names, but do not use pylint's --extension-pkg-allow-list option
# so that these names will be assumed present without having to compile and install.
# pylint: disable=no-name-in-module, import-error
from LinguaFrancami import (
    Tag, action_capsule_t, port_capsule, request_stop, schedule_copy, start
)
# pylint: disable=c-extension-no-member
import LinguaFrancami as lf
try:
    from LinguaFrancaBase.constants import BILLION, FOREVER, NEVER, instant_t, interval_t
    from LinguaFrancaBase.functions import (
        DAY, DAYS, HOUR, HOURS, MINUTE, MINUTES, MSEC, MSECS, NSEC, NSECS, SEC, SECS, USEC,
        USECS, WEEK, WEEKS
    )
    from LinguaFrancaBase.classes import Make
except ModuleNotFoundError:
    print("No module named 'LinguaFrancaBase'. "
          "Install using \"pip3 install LinguaFrancaBase\".")
    sys.exit(1)
import copy

# From the preamble, verbatim:
xt = list(range(0,10000,1000))
yt = list(range(0,10000,1000))
# End of preamble.


# Python class for reactor mi_main
class _mi_main:
    # Constructor
    def __init__(self, **kwargs):
        # Define parameters and their default values
        # Handle parameters that are set in instantiation
        self.__dict__.update(kwargs)
        # Define state variables
    
    @property
    def bank_index(self):
        return self._bank_index # pylint: disable=no-member
    
    

# Python class for reactor Node
class _Node:
    # From the preamble, verbatim:
    import random
    import numpy as np
    from reedsolo import RSCodec
    import matplotlib.pyplot as plt
    # End of preamble.
    # Constructor
    def __init__(self, **kwargs):
        # Define parameters and their default values
        self._num_nodes = 10
        self._xi = 0
        self._yi = 0
        self._bank_index = 0
        # Handle parameters that are set in instantiation
        self.__dict__.update(kwargs)
        # Define state variables
        self.a = []
        self.wf = []
        self.rsc = []
        self.x = self.xi
        self.y = self.yi
        self.index = self.bank_index
        self.k = 3
    
    @property
    def num_nodes(self):
        return self._num_nodes # pylint: disable=no-member
    
    
    @property
    def xi(self):
        return self._xi # pylint: disable=no-member
    
    
    @property
    def yi(self):
        return self._yi # pylint: disable=no-member
    
    
    @property
    def bank_index(self):
        return self._bank_index # pylint: disable=no-member
    
    
    def reaction_function_0(self):
        import funs
        
        self.a = funs.test()
        self.a.x = self.xi
        self.a.y = self.yi
        
        self.wf = funs.FSK_Generator()
        self.rsc = self.RSCodec(2)  #Reed Solomon Encoder
        return 0
    def reaction_function_1(self, tx):
        #Send data to each node
        if(self.random.random()*10 > 6):
            arr = self.np.random.rand(10)
            arr[0] = self.index + 0.001
        
            self.a.msg = arr
            for i in range(len(tx)):
                tx[i].set(self.a)
        return 0
    def reaction_function_2(self, rx):
        #This is where I check distances to see if its worth calculating waveform
        comb = []
        
        for i in range(len(rx)):
            if i != self.index and rx[i].is_present:
                dist = (abs(rx[i].value.x - self.x)**2 + abs(rx[i].value.y - self.y)**2)**(1/2)
        
                #Generate waveform with noise and multipath
                bit_array = self.wf.float_to_bit_array(rx[i].value.msg,self.rsc,encode=True)
                tmp_los,tmp_comb = self.wf.generate_packet_mp_d(bit_array,dist,0)
        
                print(f"The message to Node: {self.bank_index} from Node: {i} arrived the distance is {int(dist)} at time {lf.time.logical_elapsed()/1_000_000_000} s and dBm of {self.wf.path_loss(dist,dB=True)}")
        
                if len(comb) < 2:
                    comb = tmp_comb
                else:
                    comb = self.np.add(comb,tmp_comb)
        
        if len(comb) > 2:
            #Demoduate and recover
            bits = self.wf.demod(comb,plot=False)
        
            #Decode the bits with RSC
            try:
                decoded_float = self.wf.demod_to_float(bits,self.rsc,encode=True)
                print(f"Message recived from node: {int(decoded_float[0])}")
            except:
                print("Error")
        return 0



# Instantiate classes
mi_main_lf = [None] * 1
mi_nodes_lf = [None] * 6
# Start initializing mi of class mi_main
for mi_main_i in range(1):
    bank_index = mi_main_i
    mi_main_lf[0] = _mi_main(
        _bank_index = 0,
    )
    # Start initializing mi.nodes of class Node
    for mi_nodes_i in range(6):
        bank_index = mi_nodes_i
        mi_nodes_lf[mi_nodes_i] = _Node(
            _bank_index = mi_nodes_i,
            _num_nodes=6,
            _xi=xt[bank_index],
            _yi=yt[bank_index],
        )


# The main function
def main(argv):
    start(argv)

# As is customary in Python programs, the main() function
# should only be executed if the main module is active.
if __name__=="__main__":
    main(sys.argv)
