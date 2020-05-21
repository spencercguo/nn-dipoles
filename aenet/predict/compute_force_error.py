import sys
import pickle as pkl
import numpy as np

targnum = 1
targ_configs = {}
with open('predict.in', 'r') as pf:
    for pline in pf:
        if 'FILES' in pline:
            pline = next(pf)
            pls = pline.split()
            nfiles = int(pls[0])

            for i in range(nfiles):
                pline = next(pf)
                pls = pline.split()

                with open(pls[0], 'r') as cf:
                    energy = 0
                    for cline in cf:
                        if 'total energy' in cline:
                            cls = cline.split()
                            energy = float(cls[4])
                        if 'PRIMCOORD' in cline:
                            cline = next(cf)
                            cls = cline.split()
                            natoms = int(cls[0])

                            elems = ['X'] * natoms
                            forces = np.zeros((natoms, 3))

                            for i in range(natoms):
                                cline = next(cf)
                                cls = cline.split()
                                elems[i] = cls[0]
                                forces[i, :] = np.array([float(cls[-3]), float(cls[-2]), float(cls[-1])])

                            targ_configs[targnum] = {'elems': elems, 'forces': forces,
                                                     'energy': energy}
                            targnum += 1
    
pkl.dump(targ_configs, open('targconfigs.p', 'wb'))

pred_configs = {}
with open('predict.out', 'r') as f:
    for line in f:
        try:
            if 'Structure number' in line:
                ls = line.split()
                strucnum = int(ls[-1])

                line = next(f)  # File name
                line = next(f)  # Number of atoms

                ls = line.split()
                natoms = int(ls[-1])

                line = next(f)  # Number of species
                line = next(f)  #
                line = next(f)  # Lattice vectors
                line = next(f)  #
                line = next(f)  # a = (..., ..., ...)
                line = next(f)  # b = (..., ..., ...)
                line = next(f)  # c = (..., ..., ...)
                line = next(f)  #
                line = next(f)  # Cartesian atomic coordinates...
                line = next(f)  #
                line = next(f)  # x y z Fx Fy Fz
                line = next(f)  # (Ang) ...
                line = next(f)  # ----- ...

                elems = ['X'] * natoms
                forces = np.zeros((natoms, 3))

                for i in range(natoms):
                    line = next(f)
                    ls = line.split()
                    elems[i] = ls[0]
                    forces[i,:] = np.array([float(ls[-3]), float(ls[-2]), float(ls[-1])])

                line = next(f)  #
                line = next(f)  # Cohesive energy
                line = next(f)  # Total energy

                ls = line.split()
                energy = float(ls[-2])

                pred_configs[strucnum] = {'elems': elems, 'forces': forces,
                                          'energy': energy}
        except:
            break

pkl.dump(pred_configs, open('predconfigs.p', 'wb'))

testset_mask = np.zeros(len(pred_configs))
with open('train.out', 'r') as f:
    line = next(f)
    while 'Testing set' not in line:
        line = next(f)

    line = next(f)
    for line in f:
        ls = line.split()
        if len(ls) == 0: break
        for num in ls:
            testset_mask[int(num)-1] = 1

ntrain, ntest = 0, 0
etrain_sum_sqdiff, etest_sum_sqdiff = 0, 0
train_sum_sqdiff, train_tot_atoms = 0, 0
test_sum_sqdiff, test_tot_atoms = 0, 0
for key in pred_configs.keys():
    if testset_mask[key-1]:
        ntest += 1
        test_tot_atoms += len(pred_configs[key]['elems'])
        test_sum_sqdiff += np.sum(np.square(pred_configs[key]['forces'] - targ_configs[key]['forces']))
        etest_sum_sqdiff += np.square((pred_configs[key]['energy'] - targ_configs[key]['energy']) / len(pred_configs[key]['elems']))
    else:
        ntrain += 1
        train_tot_atoms += len(pred_configs[key]['elems'])
        train_sum_sqdiff += np.sum(np.square(pred_configs[key]['forces'] - targ_configs[key]['forces']))
        etrain_sum_sqdiff += np.square((pred_configs[key]['energy'] - targ_configs[key]['energy'])/ len(pred_configs[key]['elems']))

# force_rmse_train = np.sqrt(train_sum_sqdiff / train_tot_atoms) * 27.2114 * 1000 / 0.529177
# force_rmse_test = np.sqrt(test_sum_sqdiff / test_tot_atoms) * 27.2114 * 1000 / 0.529177

force_rmse_train = np.sqrt(train_sum_sqdiff / (3*train_tot_atoms))
force_rmse_test = np.sqrt(test_sum_sqdiff / (3*test_tot_atoms))

energy_rmse_train = np.sqrt(etrain_sum_sqdiff / ntrain)
energy_rmse_test = np.sqrt(etest_sum_sqdiff / ntest)

print('%.6E  %.6E' % (energy_rmse_train, energy_rmse_test))
print('%.6E  %.6E' % (force_rmse_train, force_rmse_test))
