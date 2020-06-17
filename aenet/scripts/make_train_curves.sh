#!/bin/bash

cd ~/nn-dipoles/aenet/
for i in x y z
do
    python3 python/training_curve.py dipole/run-02/train/$i/train.out fig/run-02/$i-test-error a
    python3 python/training_curve.py dipole/run-02/train/$i/train.out fig/run-02/$i-train-error True
done
