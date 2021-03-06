#!/bin/bash

for i in x y z
do
    mkdir $i
    cp train_bfgs.in $i/
    cd $i/

    echo "#!/bin/bash
#SBATCH -p hns
#SBATCH --job-name=train-$i
#SBATCH --nodes=1
#SBATCH --ntasks=20
#SBATCH --time=30:00:00
#SBATCH --mail-type=START,FAIL,END
#SBATCH --mail-user=scguo@stanford.edu

module load ifort
module load imkl
module load impi

train_exe=$HOME/aenet/bin/train.x-2.0.4-ifort_intelmpi

ln -sf $SCRATCH/aenet-water/dipole/generate-$i/water.train
srun -n 20 \$train_exe train_bfgs.in > train.out" > run03.sh

    sbatch run03.sh
    cd ..
done
