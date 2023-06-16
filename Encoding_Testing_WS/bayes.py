from skopt import Optimizer,load
import warnings
warnings.filterwarnings('ignore', message='The objective has been evaluated at this point before.')

import os
import numpy as np

class snrBayes:
    def __init__(self):
        self.Opt = []
        self.X = []
        self.Y = []
        self.ecc_options = [0,40,80]

    def init_optimizer(self):

        #Make a Bayes Model for each SNR value from o to -13
        for i in range(14):
            #acq_func_kwargs = {"kappa": 10000}

            optimizer = Optimizer(
            dimensions=[["0","40","80"]],
            base_estimator='rf',
            n_initial_points=0,
            acq_func= "gp_hedge",
            #acq_func_kwargs=acq_func_kwargs
            )

            self.Opt.append(optimizer)

    def iterate(self,tmp_snr,tmp_ecc,ack_status):

        decision = 0

        #Calculate the score based on the last value and its ECC
        cr = (200 - int(tmp_ecc))/200
        if ack_status == True:
            tmp_score = -1*cr
        else:
            tmp_score = 0


        #Above SNR of 0 all use the same
        if tmp_snr > 0:
            tmp_snr = 0
        
        #Index is abs of SNR so it indexes from 0 to 13
        index = abs(tmp_snr)

        #Give the correct model the next measured point and ask for the next value
        self.Opt[index].tell([str(tmp_ecc)],tmp_score)

        #Get next ECC value to try
        decision = self.Opt[index].ask()
        
        return int(decision[0])       

    def load_model(self):
        for file in os.listdir("model"):
            index = int(file[6:file.find(".pkl")])

            try:
                loaded_res = load('model/' + str(file))
                res = loaded_res.get_result()

                xs = res.x_iters
                ys = []
                for y in res.func_vals:
                    ys.append(np.float16(y))
                self.Opt[index].tell(xs,ys,fit=False)
                
            except:
                print("No Model Present")


#Example
if __name__ == "__main__":
    snr_data = [-11,-12,-13,-12,-10,-12,-9,-9]
    ecc_data = [0,40,40,80,0,40,40,80]
    ack_data = [True,False,False,True,True,False,False,True]

    model = snrBayes()
    model.init_optimizer()

    for i in range(len(snr_data)):

        #Get vaules for this moment in time
        tmp_snr = snr_data[i]
        tmp_ecc = ecc_data[i]
        ack_status = ack_data[i]

        print(model.iterate(tmp_snr,tmp_ecc,ack_status))