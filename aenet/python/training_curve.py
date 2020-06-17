import numpy as np
import matplotlib.pyplot as plt
import sys

test_rmse = []
train_rmse = []

infile = sys.argv[1]
outfile = sys.argv[2]
axis = infile.split('/')[0]
with open(infile, mode='r') as f:
    for i in range(461):
        line = next(f)
    while line:
        test_rmse.append(float(line.split()[-2]))
        train_rmse.append(float(line.split()[2]))
        try:
            line = next(f)
        except StopIteration:
            break

        
test_rmse = np.array(test_rmse)
train_rmse = np.array(train_rmse)

if not (sys.argv[3] == 'True'):
    plt.plot(test_rmse)
    plt.xlabel('Epoch')
    plt.ylabel('Test RMSE, y-component')
    plt.ylim([min(test_rmse) - 0.0005, max(test_rmse)])
    plt.savefig(f'{outfile}', dpi=200)
else:
    plt.plot(train_rmse)
    plt.xlabel('Epoch')
    plt.ylabel(f'Train RMSE, {axis}')
    plt.ylim([min(train_rmse) - 0.0005, max(train_rmse)])
    plt.savefig(f'{outfile}', dpi=200)

