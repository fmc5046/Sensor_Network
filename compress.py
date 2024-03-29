import zlib
import bz2
import gzip
import lzma
import struct
from reedsolo import RSCodec, ReedSolomonError
import fpzip
import pyzfp
import array
from reedsolo import RSCodec, ReedSolomonError
import numpy as np

def compress_data(array,operation,algorithm,size,type,lvl = 6, encode = False,precision = 14,tolerance = 0.0000001):

    #For zlib (DEFLATE)
    if algorithm == "zlib":
        if operation == "c":
            array = bytearray(array)
            result = zlib.compress(array,level=lvl)
        elif operation == "d":
            tmp_result = zlib.decompress(array)
            tmp_result = pad(tmp_result)
            result = np.frombuffer(tmp_result)

    #For BZ2
    if algorithm == "bz2":
        if operation == "c":
            array = bytearray(array)
            result = bz2.compress(array,compresslevel=lvl)
        elif operation == "d":
            tmp_result = bz2.decompress(array)
            tmp_result = pad(tmp_result)
            result = np.frombuffer(tmp_result)
        
    #For gzip
    if algorithm == "gzip":
        if operation == "c":
            array = bytearray(array)
            result = gzip.compress(array,compresslevel=lvl)
        elif operation == "d":
            tmp_result = gzip.decompress(array)
            result = np.frombuffer(tmp_result)

    #For LZMA
    if algorithm == "lzma":
        if operation == "c":
            array = bytearray(array)
            result = lzma.compress(array,check=lzma.CHECK_NONE,preset=lvl)
        elif operation == "d":
            tmp_result = lzma.decompress(array)
            tmp_result = pad(tmp_result)
            result = np.frombuffer(tmp_result)

    #For fpzip
    if algorithm == "fpzip":
        if operation == "c":
            result = fpzip.compress(array,precision=precision, order='F')
        elif operation == "d":
            array = bytes(array)
            tmp_result = fpzip.decompress(array, order='F') 
            result = tmp_result.flatten()

    #For zfp
    if algorithm == "zfp":
        if operation == "c":
            result = pyzfp.compress(array,tolerance=tolerance)
        elif operation == "d":
            array = bytes(array)
            tmp_result = pyzfp.decompress(array,size,type,tolerance=tolerance) 
            result = tmp_result.flatten()

    #For none
    if algorithm == "none":
        if operation == "c":
            array = bytearray(array)
            result = gzip.compress(array,compresslevel=0)
        elif operation == "d":
            tmp_result = gzip.decompress(array,compresslevel=0)
            result = np.frombuffer(tmp_result)

    return result


def pad(data):
    while len(data)%8 != 0:
        data = data + b'\00'
    return data 

def sim_channel(data_in,error_percent):

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


def compress_encode_packet(tmp,precision,time_stamp,data_sqn,rsc):
    #Now compress
    compressed = compress_data(tmp,'c','fpzip',1,1,precision=precision)
    #compressed = compress_data(tmp,'c','gzip',1,1,precision=precision,lvl=1)
    
    #recovered = compress_data(compressed,'d','fpzip',1,1,precision=precision)
    #recovered = compress_data(compressed,'d','gzip',1,1,precision=precision,lvl=1)
    #calc_ber(tmp,recovered)

    #This is where I add the info on the compression value
    ba = bytearray(struct.pack("d", time_stamp))
    ba[-7] = precision
    ba[-8] = data_sqn

    tmp = array.array("d",ba)
    time_stamp = tmp[0] 

    compressed = compressed + struct.pack('<d', time_stamp)

    #Now RS encode
    data = rsc.encode(compressed)

    #print(data)

    return data


def get_data_new(read_serial):
	#s = str(read_serial, 'UTF-8')
	s = read_serial

	tmp = []
	for i in s:
		tmp.append(i)

	n = 2
	my_list = [s[i:i+n] for i in range(0, len(s), n)]
	my_list = my_list[:-1]

	int_list = []
	for i in my_list:
		int_list.append(int(i,16))

	return int_list

def decompress_packet(s,ecc_sym):
    #Get the timestamp
    #print(s)
    sucess = False
    tmp_ecc = 0
    try:
        rsc = RSCodec(ecc_sym)  # ecc symbols
        a = rsc.decode(s)[0]  # original
        sucess = True
        tmp_ecc = ecc_sym
    except:
        try:
            rsc = RSCodec(36)  # ecc symbols
            a = rsc.decode(s)[0]  # original
            sucess = True
            tmp_ecc = 36
        except:
            #print(s)
            print("Error Decoding")

    if sucess == True:
        #Get the packet precision
        encoded_time = a[len(a)-8:]
        latest_timestamp = struct.unpack('<d',encoded_time)[0]
        ba = bytearray(struct.pack("d", latest_timestamp)) 
        #Get information on precision
        packet_prec = ba[-7]

        #Now decompress try both for adaptive compression scheme
        decompress = compress_data(a[:-8],'d',"fpzip",1,1,precision=packet_prec)
        #decompress = compress_data(a[:-8],'d',"gzip",1,1,precision=packet_prec,lvl=0)

        print(f"{len(decompress)} with decompression level of {packet_prec} and ecc of {tmp_ecc}")
    else:
        decompress = []

    return decompress

def calc_ber(original,recovered):
    count = 0
    leng = 0

    for i in range(len(original)):
        count += count_bit_differences(original[i],recovered[i])
        leng += 64

    print(float(count)/float(leng))

    return count,len

def count_bit_differences(a, b):
    # Convert the floating point numbers to bytes
    a_bytes = struct.pack('>f', a)
    b_bytes = struct.pack('>f', b)
    
    # Convert the bytes to integers
    a_int = int.from_bytes(a_bytes, byteorder='big')
    b_int = int.from_bytes(b_bytes, byteorder='big')
    
    # Count the number of differing bits
    difference = a_int ^ b_int
    count = 0
    while difference:
        count += difference & 1
        difference >>= 1
    
    return count

