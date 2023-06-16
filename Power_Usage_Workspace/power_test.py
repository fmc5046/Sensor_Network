import pyRAPL
import soundfile as sf
import fpzip
import time
import numpy as np


pyRAPL.setup() 

csv_output = pyRAPL.outputs.CSVOutput('result.csv')

@pyRAPL.measureit()
def foo():
    n = int(100)
    compress = False
    print(f"Number of loops {n} and compression is {compress}")
    
    file = "/home/fred/Lingua_Franca/Recover/46__23_07_13_H3_bateero1.wav"
    data, sample_rate = sf.read(file)
    array = data[:60]

    cr = []


    for _ in range(n):
        # Instructions to be evaluated.
        if compress == True:
            result = fpzip.compress(array,precision=24, order='F')

            tmp_result = fpzip.decompress(result, order='F') 
            result = tmp_result.flatten()

            len_orig = float(len(bytearray(array)))
            len_compress = float(len(bytearray(result)))
            cr.append(len_orig/len_compress)

        time.sleep(0.1)

    print(np.mean(cr))



foo()
