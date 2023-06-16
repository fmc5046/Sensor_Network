from sklearn import svm

class snrSVM:
    def __init__(self):
        self.Opt = []
        self.X = []
        self.Y = []
        self.ecc_options = [0,40,80]

    def iterate(self,snr,ecc,ack_status):
        decision = 0

        cr = (200 - ecc)/200
        self.X.append([snr, ecc])

        if ack_status == True:
            self.Y.append(cr)
        else:
            self.Y.append(0)

        regr = svm.SVR()

        if len(self.X) > 1:

            regr.fit(self.X, self.Y)
            best_pred = 0
            #Check all ECC options to select the one that predicts the best score
            for ecc_pick in self.ecc_options:

                pred = regr.predict([[snr, ecc_pick]])
                #print(f"For an ECC of {ecc_pick} the predicted is {pred}")

                if pred > best_pred:
                    decision = ecc_pick
                    best_pred = pred
        
        return decision       

#Example
if __name__ == "__main__":
    snr_data = [-110,-112,-114,-115,-110,-112,-114,-115]
    ecc_data = [0,40,40,80,0,40,40,80]
    ack_data = [True,False,False,True,True,False,False,True]

    model = snrSVM()

    for i in range(len(snr_data)):
        model.iterate(snr_data[i],ecc_data[i],ack_data[i])