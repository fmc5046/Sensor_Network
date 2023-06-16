import serial
import matplotlib.pyplot as plt

ser = serial.Serial('/dev/ttyACM1', 9600) # Replace 9600 with your baud rate

ratio = []
rssi = []
snr = []
num = []
num_error = []

try:
    while True:
        data = ser.readline().decode('utf-8').rstrip()
        values = [float(x) for x in data.split(',')]
        print(values)

        ratio.append(values[0])
        rssi.append(values[1])
        snr.append(values[2])
        num.append(values[3])
        num_error.append(values[5])

except KeyboardInterrupt:
    plt.figure()
    plt.plot(rssi)
    plt.title("RSSI vs. Time")

    plt.figure()
    plt.scatter(rssi,snr)
    plt.title("RSSI vs. SNR")

    plt.figure()
    plt.hist(num_error)

    plt.show()




