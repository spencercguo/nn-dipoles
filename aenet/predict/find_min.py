import sys
import math
import numpy as np

def read_data(filename):
    start = False
    epochs, train, test  = [], [], []
    with open(filename, 'r') as f:
        for line in f:
            ls = line.split()
            if (len(ls) > 0 and ls[0] == 'epoch'):
                start = True
                continue
            elif (len(ls) == 0 and start):
                break
            elif (start):
                epochs.append(int(ls[0]))
                train.append(float(ls[2]))
                test.append(float(ls[4]))

    return np.array(epochs), np.array(train), np.array(test)


if __name__ == "__main__":

    min_folder = " "
    min_epoch = 0
    min_test = math.inf
    for filename in sys.argv[1:]:
        epochs, train, test = read_data(filename)
        index = np.argmin(test[1:])

        if test[index+1] <= min_test:
            min_folder = filename[:-len('train.out')]
            min_epoch = epochs[index+1]
            min_test = test[index+1]

    print( min_folder + '*.ann-' + '0'*(5-len( str(min_epoch) )) + str(min_epoch) )
