import serial
import matplotlib.pyplot as plt
import bayes
import csv
import datetime
from skopt import dump

ser = serial.Serial('/dev/ttyACM0', 9600) # Replace 9600 with your baud rate

ratio = []
rssi = []
snr = []
num = []
rep = []
num_error = []
num_byte_error = []
suc = []
all_ecc = []

model = bayes.snrBayes()
model.init_optimizer()
ecc_choice = 0

try:
    while True:
        data = ser.readline().decode('utf-8').rstrip()
        try:
            values = [float(x) for x in data.split(',')]
            print(values)

            ratio.append(values[0])
            rssi.append(values[1])
            snr.append(values[2])
            num.append(values[3])
            rep.append(values[4])
            num_byte_error.append(values[5])

            #Add the Optimizer here
            #Initialize values for the SVR here
            tmp_snr = float(values[2])
            tmp_num_error = float(values[5])

            #Check if message transmission would have been successful based on choices used
            if tmp_num_error > (ecc_choice/2):
                ack = False
            else:
                ack = True
            suc.append(ack)

            #Iterate the SVR
            ecc_choice = model.iterate(tmp_snr,ecc_choice,ack)
            print(f"New ECC Choice is {ecc_choice}")

            all_ecc.append(ecc_choice)

        except:
            print("error")

#The interupt to plot the data
except:
    combined_list = list(zip(ratio,rssi,snr,num,rep,num_byte_error,suc,all_ecc))

    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    filename = "data_" + timestamp + ".csv"

    # Open CSV file for writing
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        # Write data to CSV file
        for row in combined_list:
            csvwriter.writerow(row)

    print("Data saved to file:", filename)

    for i in range(len(model.Opt)):
        res = model.Opt[i]
        dump(res, 'model/result' + str(i) + '.pkl')

    print("Models Saved!")

    plt.figure()
    plt.scatter(snr,num_byte_error)
    plt.title("RSSI vs. Time")
    plt.show()



