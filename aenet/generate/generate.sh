#!/bin/bash

for i in x y z 
do
    cd generate-$i
    sbatch run02-${i}.sh
    cd ..
done
